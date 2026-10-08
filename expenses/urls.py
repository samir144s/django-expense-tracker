from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    # Dashboard
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    # Add expense
    path(
        'add-expense/',
        views.add_expense,
        name='add_expense'
    ),

    # Edit expense
    path(
        'edit-expense/<int:expense_id>/',
        views.edit_expense,
        name='edit_expense'
    ),

    # Delete expense
    path(
        'delete-expense/<int:expense_id>/',
        views.delete_expense,
        name='delete_expense'
    ),
    # All expenses
    path(
        'expenses/',
        views.all_expenses,
        name='all_expenses'
    ),
        # Categories
    path(
        'categories/',
        views.categories,
        name='categories'
    ),

    # Add category
    path(
        'add-category/',
        views.add_category,
        name='add_category'
    ),
    # Edit category
    path(
        'edit-category/<int:category_id>/',
        views.edit_category,
        name='edit_category'
    ),

    # Delete category
    path(
        'delete-category/<int:category_id>/',
        views.delete_category,
        name='delete_category'
    ),
    # Reports
    path(
        'reports/',
        views.reports,
        name='reports'
    ),
    # Account Settings
    path(
        'settings/',
        views.account_settings,
        name='account_settings'
    ),

    # Register
    path(
        'register/',
        views.register_view,
        name='register'
    ),

    # Login
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='expenses/login.html'
        ),
        name='login'
    ),

    # Logout
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

]