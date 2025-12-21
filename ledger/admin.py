from django.contrib import admin
from .models import Category, Subcategory, Expense

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'category', 'subcategory', 'description', 'user')
    list_filter = ('user', 'category', 'subcategory', 'date')
    search_fields = ('description',)
    date_hierarchy = 'date'
