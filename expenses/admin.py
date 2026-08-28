from django.contrib import admin
from .models import Expense, Income, Category, Budget, Notification, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'user']
    list_filter = ['user']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'category', 'date', 'user']
    list_filter = ['category', 'user', 'date']
    search_fields = ['title', 'notes']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'category', 'date', 'user', 'recurring']
    list_filter = ['category', 'user', 'recurring']
    search_fields = ['title', 'notes']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'limit', 'month', 'year', 'user']
    list_filter = ['user', 'year', 'month']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'read', 'user', 'created_at']
    list_filter = ['type', 'read', 'user']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'theme']
