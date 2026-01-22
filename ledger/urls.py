
from django.urls import path
from . import views

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
#     path('expenses/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
#     path('expenses/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_update'),
#     path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
#     path('subcategories/', views.SubcategoryListView.as_view(), name='subcategory_list'),
#     path('subcategories/add/', views.subcategory_create, name='subcategory_create'),
#     path('test/', views.test_view, name='test'),
#     path('health/', views.health, name='health'),  # Health check endpoint
# ]

urlpatterns = [
    # Home / dashboard
    path('', views.dashboard, name='dashboard'),

    # Expenses CRUD
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),

    # Subcategories
    path('subcategories/', views.SubcategoryListView.as_view(), name='subcategory_list'),
    path('subcategories/add/', views.subcategory_create, name='subcategory_create'),

    # Misc
    path('test/', views.test_view, name='test'),

    # Health (keep /health for compatibility)
    path('health/', views.health, name='health'),
    
    # Keepalive endpoint for session management
    path('keepalive/', views.keepalive, name='keepalive'),
]