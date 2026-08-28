from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Sum
from django.contrib.auth.hashers import check_password
from .models import Expense, Income, Category, Budget, Notification, UserProfile
from .serializers import (
    ExpenseSerializer, IncomeSerializer, CategorySerializer,
    BudgetSerializer, NotificationSerializer, UserSerializer, UserProfileSerializer
)


class SignupView(APIView):
    """Register a new user. Creates default categories and profile."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """Get and update user profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        data = serializer.data
        data['name'] = request.user.get_full_name() or request.user.username
        data['email'] = request.user.email
        data['avatar'] = (request.user.first_name or request.user.username)[0].upper()
        data['is_admin'] = request.user.is_staff
        return Response(data)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if 'name' in request.data:
            request.user.first_name = request.data['name']
            request.user.save()
        if 'email' in request.data:
            request.user.email = request.data['email']
            request.user.save()
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response({'message': 'Profile updated'})


class DashboardView(APIView):
    """Aggregated dashboard data in a single API call."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        total_expense = Expense.objects.filter(user=user).aggregate(t=Sum('amount'))['t'] or 0
        total_income = Income.objects.filter(user=user).aggregate(t=Sum('amount'))['t'] or 0
        balance = float(total_income) - float(total_expense)

        recent_expenses = ExpenseSerializer(
            Expense.objects.filter(user=user)[:5], many=True
        ).data

        recent_incomes = IncomeSerializer(
            Income.objects.filter(user=user)[:5], many=True
        ).data

        # Category breakdown for expenses
        cat_breakdown = (
            Expense.objects.filter(user=user)
            .values('category')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        unread_notifs = Notification.objects.filter(user=user, read=False).count()

        return Response({
            'total_expense': float(total_expense),
            'total_income': float(total_income),
            'balance': balance,
            'recent_expenses': recent_expenses,
            'recent_incomes': recent_incomes,
            'category_breakdown': list(cat_breakdown),
            'unread_notifications': unread_notifs,
        })


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Expense.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        expense = serializer.save(user=self.request.user)
        # Check budget and create notification if exceeded
        from datetime import date
        today = date.today()
        budget = Budget.objects.filter(
            user=self.request.user,
            category=expense.category,
            month=today.month,
            year=today.year
        ).first()
        if budget:
            spent = Expense.objects.filter(
                user=self.request.user,
                category=expense.category,
                date__month=today.month,
                date__year=today.year
            ).aggregate(t=Sum('amount'))['t'] or 0
            if float(spent) > float(budget.limit):
                Notification.objects.create(
                    user=self.request.user,
                    type='error',
                    title='Budget Exceeded!',
                    text=f'{expense.category} budget exceeded! Spent ₹{spent} of ₹{budget.limit} limit.'
                )
            elif float(spent) >= float(budget.limit) * 0.8:
                Notification.objects.create(
                    user=self.request.user,
                    type='warning',
                    title='Budget Alert',
                    text=f'{expense.category} budget is at {int(float(spent)/float(budget.limit)*100)}% usage.'
                )


class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Income.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        income = serializer.save(user=self.request.user)
        Notification.objects.create(
            user=self.request.user,
            type='success',
            title='Income Received',
            text=f'₹{income.amount} received from {income.title}.'
        )


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({'message': 'All notifications marked as read'})

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.read = True
        notif.save()
        return Response({'message': 'Marked as read'})


class ChangePasswordView(APIView):
    """Change the authenticated user's password."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(old_password, request.user.password):
            return Response(
                {'error': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {'error': 'New password must be at least 8 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': 'Password updated successfully.'})
