from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.core.paginator import Paginator

from .forms import RegisterForm, ExpenseForm
from .models import Expense, Category


# ==========================================
# REGISTER
# ==========================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            messages.success(
                request,
                'Account created successfully!'
            )

            return redirect('dashboard')

    else:

        form = RegisterForm()

    return render(
        request,
        'expenses/register.html',
        {
            'form': form
        }
    )


# ==========================================
# DASHBOARD
# ==========================================

def dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user

    # Total expenses
    total_expenses = Expense.objects.filter(
        user=user
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Current date
    today = timezone.now().date()

    # Monthly expenses
    monthly_expenses = Expense.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Total transactions
    transaction_count = Expense.objects.filter(
        user=user
    ).count()

    # Total categories
    category_count = Category.objects.filter(
        user=user
    ).count()

    # Recent expenses
    recent_expenses = Expense.objects.filter(
        user=user
    ).select_related(
        'category'
    ).order_by(
        '-date',
        '-created_at'
    )[:5]

    context = {

        'total_expenses': total_expenses,

        'monthly_expenses': monthly_expenses,

        'transaction_count': transaction_count,

        'category_count': category_count,

        'recent_expenses': recent_expenses,

    }

    return render(
        request,
        'expenses/dashboard.html',
        context
    )


# ==========================================
# ADD EXPENSE
# ==========================================

def add_expense(request):

    if not request.user.is_authenticated:
        return redirect('login')

    # Default categories
    default_categories = [

        'Food',

        'Transport',

        'Bills',

        'Shopping',

        'Education',

        'Health',

        'Entertainment',

        'Other',

    ]

    # Create categories automatically
    for category_name in default_categories:

        Category.objects.get_or_create(
            user=request.user,
            name=category_name
        )

    if request.method == 'POST':

        form = ExpenseForm(request.POST)

        # Only show user's categories
        form.fields['category'].queryset = Category.objects.filter(
            user=request.user
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.user = request.user

            expense.save()

            messages.success(
                request,
                'Expense added successfully!'
            )

            return redirect('dashboard')

    else:

        form = ExpenseForm()

        # Only show user's categories
        form.fields['category'].queryset = Category.objects.filter(
            user=request.user
        )

    return render(
        request,
        'expenses/add_expense.html',
        {
            'form': form
        }
    )


# ==========================================
# EDIT EXPENSE
# ==========================================

def edit_expense(request, expense_id):

    if not request.user.is_authenticated:
        return redirect('login')

    # Only allow user to edit their own expense
    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == 'POST':

        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        # Only show user's categories
        form.fields['category'].queryset = Category.objects.filter(
            user=request.user
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.user = request.user

            expense.save()

            messages.success(
                request,
                'Expense updated successfully!'
            )

            return redirect('dashboard')

    else:

        form = ExpenseForm(
            instance=expense
        )

        # Only show user's categories
        form.fields['category'].queryset = Category.objects.filter(
            user=request.user
        )

    return render(
        request,
        'expenses/edit_expense.html',
        {
            'form': form,
            'expense': expense
        }
    )


# ==========================================
# DELETE EXPENSE
# ==========================================

def delete_expense(request, expense_id):

    if not request.user.is_authenticated:
        return redirect('login')

    # Only allow user to delete their own expense
    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == 'POST':

        expense.delete()

        messages.success(
            request,
            'Expense deleted successfully!'
        )

        return redirect('dashboard')

    return render(
        request,
        'expenses/delete_expense.html',
        {
            'expense': expense
        }
    )


# ==========================================
# ALL EXPENSES
# ==========================================

def all_expenses(request):

    if not request.user.is_authenticated:
        return redirect('login')

    # Get only the logged-in user's expenses
    expenses = Expense.objects.filter(
        user=request.user
    ).select_related(
        'category'
    ).order_by(
        '-date',
        '-created_at'
    )

    # ==========================================
    # SEARCH
    # ==========================================

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        expenses = expenses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # ==========================================
    # CATEGORY FILTER
    # ==========================================

    category_id = request.GET.get(
        'category',
        ''
    )

    if category_id:

        expenses = expenses.filter(
            category_id=category_id
        )

    # ==========================================
    # DATE FILTER
    # ==========================================

    date = request.GET.get(
        'date',
        ''
    )

    if date:

        expenses = expenses.filter(
            date=date
        )

    # ==========================================
    # CATEGORIES
    # ==========================================

    categories = Category.objects.filter(
        user=request.user
    ).order_by(
        'name'
    )

    # ==========================================
    # PAGINATION
    # ==========================================

    paginator = Paginator(
        expenses,
        10
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    # ==========================================
    # TOTAL FILTERED EXPENSE
    # ==========================================

    filtered_total = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {

        'expenses': page_obj,

        'page_obj': page_obj,

        'categories': categories,

        'filtered_total': filtered_total,

        'search': search,

        'selected_category': category_id,

        'selected_date': date,

    }

    return render(
        request,
        'expenses/all_expenses.html',
        context
    )

# ==========================================
# CATEGORY LIST
# ==========================================

def categories(request):

    if not request.user.is_authenticated:
        return redirect('login')

    user_categories = Category.objects.filter(
        user=request.user
    ).annotate(
        expense_count=Count('expense'),
        total_spent=Sum('expense__amount')
    ).order_by('name')

    return render(
        request,
        'expenses/categories.html',
        {
            'categories': user_categories
        }
    )
# ==========================================
# ADD CATEGORY
# ==========================================

def add_category(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        if name:

            Category.objects.get_or_create(
                user=request.user,
                name=name
            )

            messages.success(
                request,
                'Category added successfully!'
            )

            return redirect('categories')

        messages.error(
            request,
            'Please enter a category name.'
        )

    return redirect('categories')


# ==========================================
# DELETE CATEGORY
# ==========================================

def delete_category(request, category_id):

    if not request.user.is_authenticated:
        return redirect('login')

    category = get_object_or_404(
        Category,
        id=category_id,
        user=request.user
    )

    if request.method == 'POST':

        # Check whether this category is being used
        # by any of the user's expenses
        if Expense.objects.filter(
            category=category,
            user=request.user
        ).exists():

            messages.error(
                request,
                'This category cannot be deleted because it is being used by one or more expenses.'
            )

            return redirect('categories')

        category.delete()

        messages.success(
            request,
            'Category deleted successfully!'
        )

        return redirect('categories')

    return redirect('categories')
# ==========================================
# EDIT CATEGORY
# ==========================================

def edit_category(request, category_id):

    if not request.user.is_authenticated:
        return redirect('login')

    category = get_object_or_404(
        Category,
        id=category_id,
        user=request.user
    )

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        if not name:

            messages.error(
                request,
                'Please enter a category name.'
            )

            return redirect(
                'edit_category',
                category_id=category.id
            )

        # Check if another category with the same
        # name already exists for this user
        if Category.objects.filter(
            user=request.user,
            name=name
        ).exclude(
            id=category.id
        ).exists():

            messages.error(
                request,
                'You already have a category with this name.'
            )

            return redirect(
                'edit_category',
                category_id=category.id
            )

        category.name = name
        category.save()

        messages.success(
            request,
            'Category updated successfully!'
        )

        return redirect('categories')

    return render(
        request,
        'expenses/edit_category.html',
        {
            'category': category
        }
    )
# ==========================================
# REPORTS
# ==========================================

def reports(request):

    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user

    # ==========================================
    # REPORT FILTER
    # ==========================================

    report_filter = request.GET.get(
        'filter',
        'all'
    )

    today = timezone.now().date()

    expenses = Expense.objects.filter(
        user=user
    )


    # ==========================================
    # APPLY FILTER
    # ==========================================

    if report_filter == 'this_month':

        expenses = expenses.filter(
            date__year=today.year,
            date__month=today.month
        )

    elif report_filter == 'last_month':

        if today.month == 1:

            last_month = 12
            last_month_year = today.year - 1

        else:

            last_month = today.month - 1
            last_month_year = today.year

        expenses = expenses.filter(
            date__year=last_month_year,
            date__month=last_month
        )

    elif report_filter == 'this_year':

        expenses = expenses.filter(
            date__year=today.year
        )


    # ==========================================
    # TOTAL SPENDING
    # ==========================================

    total_expenses = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0


    # ==========================================
    # TOTAL TRANSACTIONS
    # ==========================================

    transaction_count = expenses.count()


    # ==========================================
    # SPENDING BY CATEGORY
    # ==========================================

    category_report = Category.objects.filter(
        user=user
    ).annotate(
        total_spent=Sum(
            'expense__amount',
            filter=Q(
                expense__in=expenses
            )
        ),
        expense_count=Count(
            'expense',
            filter=Q(
                expense__in=expenses
            )
        )
    ).order_by(
        '-total_spent'
    )


    # ==========================================
    # CATEGORY CHART DATA
    # ==========================================

    chart_labels = []
    chart_values = []

    for category in category_report:

        if category.total_spent:

            chart_labels.append(
                category.name
            )

            chart_values.append(
                float(category.total_spent)
            )


    # ==========================================
    # MONTHLY SPENDING
    # ==========================================

    monthly_data = expenses.values(
        'date__year',
        'date__month'
    ).annotate(
        total=Sum('amount')
    ).order_by(
        'date__year',
        'date__month'
    )


    # ==========================================
    # MONTHLY CHART DATA
    # ==========================================

    month_labels = []
    month_values = []

    month_names = [
        '',
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ]


    for month in monthly_data:

        year = month['date__year']

        month_number = month['date__month']

        total = month['total']

        month_labels.append(
            f"{month_names[month_number]} {year}"
        )

        month_values.append(
            float(total)
        )


    # ==========================================
    # DAILY SPENDING
    # ==========================================

    daily_data = expenses.values(
        'date'
    ).annotate(
        total=Sum('amount')
    ).order_by(
        'date'
    )


    # ==========================================
    # DAILY CHART DATA
    # ==========================================

    daily_labels = []
    daily_values = []

    for day in daily_data:

        daily_labels.append(
            day['date'].strftime('%d %b %Y')
        )

        daily_values.append(
            float(day['total'])
        )


    # ==========================================
    # CONTEXT
    # ==========================================

    context = {

        'total_expenses': total_expenses,

        'transaction_count': transaction_count,

        'category_report': category_report,


        # Category chart
        'chart_labels': chart_labels,
        'chart_values': chart_values,


        # Monthly chart
        'month_labels': month_labels,
        'month_values': month_values,


        # Daily chart
        'daily_labels': daily_labels,
        'daily_values': daily_values,


        # Filter
        'report_filter': report_filter,

    }


    return render(
        request,
        'expenses/reports.html',
        context
    )
# ==========================================
# ACCOUNT SETTINGS
# ==========================================

def account_settings(request):

    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user

    password_form = PasswordChangeForm(user)

    # Add Bootstrap styling to password fields
    for field in password_form.fields.values():
        field.widget.attrs.update({
            'class': 'form-control'
        })

    if request.method == 'POST':

        action = request.POST.get('action')

        # ==========================================
        # UPDATE PROFILE
        # ==========================================

        if action == 'profile':

            username = request.POST.get(
                'username',
                ''
            ).strip()

            email = request.POST.get(
                'email',
                ''
            ).strip()

            if not username:

                messages.error(
                    request,
                    'Username cannot be empty.'
                )

                return redirect(
                    'account_settings'
                )

            if User.objects.filter(
                username=username
            ).exclude(
                id=user.id
            ).exists():

                messages.error(
                    request,
                    'This username is already taken.'
                )

                return redirect(
                    'account_settings'
                )

            user.username = username
            user.email = email

            user.save()

            messages.success(
                request,
                'Account information updated successfully!'
            )

            return redirect(
                'account_settings'
            )

        # ==========================================
        # CHANGE PASSWORD
        # ==========================================

        elif action == 'password':

            password_form = PasswordChangeForm(
                user,
                request.POST
            )

            for field in password_form.fields.values():
                field.widget.attrs.update({
                    'class': 'form-control'
                })

            if password_form.is_valid():

                updated_user = password_form.save()

                # Keep user logged in after password change
                update_session_auth_hash(
                    request,
                    updated_user
                )

                messages.success(
                    request,
                    'Password changed successfully!'
                )

                return redirect(
                    'account_settings'
                )

    return render(
        request,
        'expenses/account_settings.html',
        {
            'user': user,
            'password_form': password_form,
        }
    )