from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Expense, Income, Category, Budget, Notification, UserProfile


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Create default categories for the new user
        default_cats = [
            ('Food', '🍔', '#E53935'),
            ('Transport', '🚗', '#5C6BC0'),
            ('Bills', '💡', '#FF9800'),
            ('Shopping', '🛍️', '#AB47BC'),
            ('Health', '🏥', '#4CAF50'),
            ('Entertainment', '🎮', '#00BCD4'),
            ('Education', '📚', '#795548'),
            ('Salary', '💰', '#4CAF50'),
            ('Freelance', '💻', '#2196F3'),
            ('Investment', '📈', '#C4944A'),
        ]
        for name, icon, color in default_cats:
            Category.objects.create(user=user, name=name, icon=icon, color=color)
        # Create user profile
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'currency', 'theme']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'color', 'created_at']
        read_only_fields = ['created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'category', 'date', 'notes', 'recurring', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'title', 'amount', 'category', 'date', 'notes', 'recurring', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = ['id', 'category', 'limit', 'month', 'year', 'spent', 'created_at']
        read_only_fields = ['created_at']

    def get_spent(self, obj):
        """Calculate actual spent from expenses for this category/month/year."""
        from django.db.models import Sum
        total = Expense.objects.filter(
            user=obj.user,
            category=obj.category,
            date__month=obj.month,
            date__year=obj.year
        ).aggregate(total=Sum('amount'))['total']
        return float(total or 0)


class NotificationSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'text', 'read', 'time', 'created_at']
        read_only_fields = ['created_at']

    def get_time(self, obj):
        from django.utils.timesince import timesince
        return f"{timesince(obj.created_at)} ago"
