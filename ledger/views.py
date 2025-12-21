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
    
    # Current month expenses
    month_expenses = Expense.objects.filter(
        user=request.user, 
        date__year=today.year, 
        date__month=today.month
    )
    total_month = month_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Today's expenses
    today_expenses = Expense.objects.filter(user=request.user, date=today)
    
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
    
    context = {
        'total_month': total_month,
        'today_expenses': today_expenses,
        'form': form,
        'today': today,
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

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'ledger/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.all()

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'ledger/category_form.html', {'form': form})

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
