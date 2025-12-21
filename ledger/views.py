from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from datetime import date
from .models import Expense, Category, Subcategory
from .forms import ExpenseForm, CategoryForm, SubcategoryForm

@login_required
def dashboard(request):
    today = date.today()
    
    # Get filter parameters from request
    selected_year = request.GET.get('year', today.year)
    selected_month = request.GET.get('month', today.month)
    
    try:
        selected_year = int(selected_year)
        selected_month = int(selected_month)
    except (ValueError, TypeError):
        selected_year = today.year
        selected_month = today.month
    
    # Current month expenses (based on filter or current month)
    month_expenses = Expense.objects.filter(
        user=request.user, 
        date__year=selected_year, 
        date__month=selected_month
    )
    total_month = month_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Today's expenses (only if current month/year is selected)
    if selected_year == today.year and selected_month == today.month:
        today_expenses = Expense.objects.filter(user=request.user, date=today)
        total_today = today_expenses.aggregate(total=Sum('amount'))['total'] or 0
    else:
        today_expenses = Expense.objects.none()
        total_today = 0
    
    # Total yearly expenses
    year_expenses = Expense.objects.filter(
        user=request.user, 
        date__year=selected_year
    )
    total_year = year_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Handle quick add
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(initial={'date': today}, user=request.user)
    
    # Generate year options (current year and previous 5 years)
    year_options = []
    for year in range(today.year, today.year - 6, -1):
        year_options.append(year)
    
    # Generate month options
    import calendar
    month_options = []
    for month in range(1, 13):
        month_options.append((month, calendar.month_name[month]))
    
    # Get selected month name
    selected_month_name = calendar.month_name[selected_month]
    
    context = {
        'total_month': total_month,
        'total_today': total_today,
        'total_year': total_year,
        'today_expenses': today_expenses,
        'month_expenses': month_expenses.order_by('-date', '-created_at')[:10],  # Recent expenses for selected month
        'form': form,
        'today': today,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,
        'year_options': year_options,
        'month_options': month_options,
        'subcategory_category_map': getattr(form, 'subcategory_category_map', {}),
    }
    return render(request, 'ledger/dashboard.html', context)

class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'ledger/expense_list.html'
    paginate_by = 20
    context_object_name = 'expenses'
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'ledger/expense_form.html'
    success_url = reverse_lazy('expense_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subcategory_category_map'] = getattr(context['form'], 'subcategory_category_map', {})
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'ledger/expense_form.html'
    success_url = reverse_lazy('expense_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subcategory_category_map'] = getattr(context['form'], 'subcategory_category_map', {})
        return context
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'ledger/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

# Category management views - commented out as per user request
# class CategoryListView(LoginRequiredMixin, ListView):
#     model = Category
#     template_name = 'ledger/category_list.html'
#     context_object_name = 'categories'
#     
#     def get_queryset(self):
#         return Category.objects.all()

# @login_required
# def category_create(request):
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('category_list')
#     else:
#         form = CategoryForm()
#     return render(request, 'ledger/category_form.html', {'form': form})

class SubcategoryListView(LoginRequiredMixin, ListView):
    model = Subcategory
    template_name = 'ledger/subcategory_list.html'
    context_object_name = 'subcategories'
    
    def get_queryset(self):
        return Subcategory.objects.all()

@login_required
def subcategory_create(request):
    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subcategory_list')
    else:
        form = SubcategoryForm()
    return render(request, 'ledger/subcategory_form.html', {'form': form})
