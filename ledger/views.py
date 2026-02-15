from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from datetime import date
import calendar
from collections import defaultdict
from .models import Expense, Category, Subcategory
from .forms import ExpenseForm, CategoryForm, SubcategoryForm
from django.http import HttpResponse,  JsonResponse, HttpResponseBadRequest
from django.utils import timezone
import json

from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from google.oauth2 import id_token
from google.auth.transport import requests as grequests
import logging
import csv

# --------------------------------------------------------------------------------------

# @login_required
# def dashboard(request):
#     today = date.today()
    
#     # Get filter parameters from request
#     selected_year = request.GET.get('year', today.year)
#     selected_month = request.GET.get('month', today.month)
    
#     try:
#         selected_year = int(selected_year)
#         selected_month = int(selected_month)
#     except (ValueError, TypeError):
#         selected_year = today.year
#         selected_month = today.month
    
#     # Current month expenses (based on filter or current month)
#     month_expenses = Expense.objects.filter(
#         user=request.user, 
#         date__year=selected_year, 
#         date__month=selected_month
#     )
#     total_month = month_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
#     # Today's expenses (only if current month/year is selected)
#     if selected_year == today.year and selected_month == today.month:
#         today_expenses = Expense.objects.filter(user=request.user, date=today)
#         total_today = today_expenses.aggregate(total=Sum('amount'))['total'] or 0
#     else:
#         today_expenses = Expense.objects.none()
#         total_today = 0
    
#     # Total yearly expenses
#     year_expenses = Expense.objects.filter(
#         user=request.user, 
#         date__year=selected_year
#     )
#     total_year = year_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
#     # Handle quick add
#     if request.method == 'POST':
#         form = ExpenseForm(request.POST, user=request.user)
#         if form.is_valid():
#             expense = form.save(commit=False)
#             expense.user = request.user
#             expense.save()
#             return redirect('dashboard')
#     else:
#         form = ExpenseForm(initial={'date': today}, user=request.user)
    
#     # Generate year options (current year and previous 5 years)
#     year_options = []
#     for year in range(today.year, today.year - 6, -1):
#         year_options.append(year)
    
#     # Generate month options
#     import calendar
#     month_options = []
#     for month in range(1, 13):
#         month_options.append((month, calendar.month_name[month]))
    
#     # Get selected month name
#     selected_month_name = calendar.month_name[selected_month]
    
#     context = {
#         'total_month': total_month,
#         'total_today': total_today,
#         'total_year': total_year,
#         'today_expenses': today_expenses,
#         'month_expenses': month_expenses.order_by('-date', '-created_at')[:10],  # Recent expenses for selected month
#         'form': form,
#         'today': today,
#         'selected_year': selected_year,
#         'selected_month': selected_month,
#         'selected_month_name': selected_month_name,
#         'year_options': year_options,
#         'month_options': month_options,
#         'subcategory_category_map': getattr(form, 'subcategory_category_map', {}),
#     }
#     return render(request, 'ledger/dashboard.html', context)

@require_http_methods(["GET", "HEAD", "POST"])   # ✅ HEAD-safe, POST for quick-add
@login_required
def dashboard(request):
    today = date.today()

    # Parse filters defensively
    selected_year = request.GET.get('year', today.year)
    selected_month = request.GET.get('month', today.month)
    try:
        selected_year = int(selected_year)
        selected_month = int(selected_month)
    except (ValueError, TypeError):
        selected_year = today.year
        selected_month = today.month

    # ✅ Month queryset: select_related to avoid N+1 in templates
    month_qs = (
        Expense.objects
        .filter(user=request.user, date__year=selected_year, date__month=selected_month)
        .select_related('category', 'subcategory')  # assumes FK names on Expense
        .only('id', 'amount', 'description', 'date', 'created_at',
              'category__id', 'category__name',
              'subcategory__id', 'subcategory__name')
    )
    total_month = month_qs.aggregate(total=Sum('amount'))['total'] or 0

    # Today's expenses only if month/year matches today
    if selected_year == today.year and selected_month == today.month:
        today_qs = (
            Expense.objects
            .filter(user=request.user, date=today)
            .select_related('category', 'subcategory')
            .only('id', 'amount', 'description', 'date', 'created_at',
                  'category__id', 'category__name',
                  'subcategory__id', 'subcategory__name')
        )
        total_today = today_qs.aggregate(total=Sum('amount'))['total'] or 0
    else:
        today_qs = Expense.objects.none()
        total_today = 0

    # Year total (aggregate only)
    total_year = (
        Expense.objects
        .filter(user=request.user, date__year=selected_year)
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    # Handle quick-add form
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(initial={'date': today}, user=request.user)

    # Year options: current and previous 5
    year_options = list(range(today.year, today.year - 6, -1))

    # Month options
    month_options = [(m, calendar.month_name[m]) for m in range(1, 13)]
    selected_month_name = calendar.month_name[selected_month]

    context = {
        'total_month': total_month,
        'total_today': total_today,
        'total_year': total_year,
        'today_expenses': today_qs,
        # ✅ Restrict the list to a small recent slice and avoid extra fetches
        'month_expenses': month_qs.order_by('-date', '-created_at')[:10],
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
# --------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------

# class ExpenseListView(LoginRequiredMixin, ListView):
#     model = Expense
#     # template_name = 'ledger/expense_list.html'
#     # paginate_by = 20
#     # context_object_name = 'expenses'
#     template_name = 'ledger/expense_pivot.html'
#     context_object_name = 'pivot_data'
    
#     def get_queryset(self):
#         # return Expense.objects.filter(user=self.request.user) Earlier code for expense_list.html
#         # Get selected year (default to current year)
#         today = date.today()
#         selected_year = self.request.GET.get('year', today.year)
#         try:
#             selected_year = int(selected_year)
#         except (ValueError, TypeError):
#             selected_year = today.year
        
#         # Get all expenses for the selected year
#         expenses = Expense.objects.filter(
#             user=self.request.user,
#             date__year=selected_year
#         )
        
#         # Create pivot data structure
#         pivot_data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
#         row_totals = defaultdict(float)
        
#         # Aggregate expenses by category, subcategory, and month
#         for expense in expenses:
#             category_name = expense.category.name if expense.category else 'Uncategorized'
#             subcategory_name = expense.subcategory.name if expense.subcategory else 'Uncategorized'
#             month = expense.date.month
#             amount = float(expense.amount)
            
#             pivot_data[category_name][subcategory_name][month] += amount
#             row_totals[f"{category_name} > {subcategory_name}"] += amount
        
#         # Prepare month names
#         month_names = []
#         for month in range(1, 13):
#             month_names.append(calendar.month_name[month])
        
#         # Prepare final data structure
#         final_data = []
#         for category, subcategories in pivot_data.items():
#             for subcategory, months in subcategories.items():
#                 row_data = {
#                     'category': category,
#                     'subcategory': subcategory,
#                     'months': [],
#                     'total': 0
#                 }
                
#                 # Add monthly amounts
#                 for month in range(1, 13):
#                     amount = months.get(month, 0)
#                     row_data['months'].append(amount)
#                     row_data['total'] += amount
                
#                 final_data.append(row_data)
        
#         # Sort data by category and subcategory
#         final_data.sort(key=lambda x: (x['category'], x['subcategory']))
        
#         # Calculate overall total for all subcategories
#         overall_total = sum(row['total'] for row in final_data)
        
#         # Calculate additional statistics
#         total_categories = len(set(row['category'] for row in final_data))
#         total_subcategories = len(final_data)
        
#         return {
#             'data': final_data,
#             'month_names': month_names,
#             'selected_year': selected_year,
#             'year_options': list(range(today.year, today.year - 6, -1)),
#             'overall_total': overall_total,
#             'total_categories': total_categories,
#             'total_subcategories': total_subcategories
#         }


class ExpenseListView(LoginRequiredMixin, TemplateView):
    template_name = 'ledger/expense_pivot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        # Parse year safely
        selected_year = self.request.GET.get('year', today.year)
        try:
            selected_year = int(selected_year)
        except (ValueError, TypeError):
            selected_year = today.year

        # ✅ DB-side aggregation: one query
        # Produces rows: category_name, subcategory_name, month (1-12), total
        qs = (
            Expense.objects
            .filter(user=self.request.user, date__year=selected_year)
            .values('category__name', 'subcategory__name')
            .annotate(month=ExtractMonth('date'))
            .values('category__name', 'subcategory__name', 'month')
            .annotate(total=Sum('amount'))
            .order_by('category__name', 'subcategory__name', 'month')
        )

        # Build pivot rows
        month_names = [calendar.month_name[m] for m in range(1, 13)]
        # {(cat, subcat): [12 monthly totals]}
        from collections import defaultdict
        grid = defaultdict(lambda: [0.0] * 12)

        for row in qs:
            cat = row['category__name'] or 'Uncategorized'
            sub = row['subcategory__name'] or 'Uncategorized'
            m = row['month'] or 0
            if 1 <= m <= 12:
                grid[(cat, sub)][m - 1] += float(row['total'] or 0)

        final_data = []
        for (cat, sub), months in grid.items():
            final_data.append({
                'category': cat,
                'subcategory': sub,
                'months': months,
                'total': sum(months),
            })

        # Sort rows by category, then subcategory
        final_data.sort(key=lambda x: (x['category'], x['subcategory']))

        overall_total = sum(r['total'] for r in final_data)
        total_categories = len({r['category'] for r in final_data})
        total_subcategories = len(final_data)
        year_options = list(range(today.year, today.year - 6, -1))

        context.update({
            'data': final_data,
            'month_names': month_names,
            'selected_year': selected_year,
            'year_options': year_options,
            'overall_total': overall_total,
            'total_categories': total_categories,
            'total_subcategories': total_subcategories,
        })
# Add `pivot_data` for your template
        context['pivot_data'] = {
            'data': final_data,
            'month_names': month_names,
            'selected_year': selected_year,
            'year_options': year_options,
            'overall_total': overall_total,
            'total_categories': total_categories,
            'total_subcategories': total_subcategories,
        }
        return context
# --------------------------------------------------------------------------------------

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

# def test_view(request):
#     return HttpResponse("Hello! This URL is working.")

# def test_view(request):
#     return render(request, 'ledger/test.html')

@login_required
# def test_view(request):

#     today = date.today()
#     current_year = today.year
#     current_month = today.month
    
#     # Get filter parameters from POST if submitted, else defaults
#     if request.method == 'POST':
#         selected_year = request.POST.get('year', str(current_year))
#         selected_month = request.POST.get('month', str(current_month))
#         selected_category = request.POST.get('category', 'all')
#     else:
#         selected_year = str(current_year)
#         selected_month = str(current_month)
#         selected_category = 'all'
    
#     try:
#         selected_year = int(selected_year)
#         selected_month = int(selected_month)
#     except (ValueError, TypeError):
#         selected_year = current_year
#         selected_month = current_month
    
#     # Get available years
#     available_years = list(Expense.objects.filter(user=request.user).dates('date', 'year').values_list('date__year', flat=True).distinct().order_by('-date__year'))
#     if current_year not in available_years:
#         available_years.append(current_year)
#     available_years.sort(reverse=True)
    
#     # Get categories that have expenses in the selected period
#     filtered_expenses = Expense.objects.filter(
#         user=request.user,
#         date__year=selected_year,
#         date__month=selected_month
#     )
#     category_ids = filtered_expenses.values_list('category_id', flat=True).distinct()
#     categories = list(Category.objects.filter(id__in=category_ids).order_by('name'))
    
#     # Filter expenses
#     expenses = Expense.objects.filter(
#         user=request.user,
#         date__year=selected_year,
#         date__month=selected_month
#     )
#     if selected_category != 'all':
#         try:
#             cat_id = int(selected_category)
#             expenses = expenses.filter(category_id=cat_id)
#         except ValueError:
#             pass
    
#     # Aggregate by subcategory for bar chart
#     data = expenses.values('subcategory__name').annotate(total=Sum('amount')).filter(total__gt=0).order_by('subcategory__name')
#     labels = [item['subcategory__name'] or 'No Subcategory' for item in data]
#     values = [float(item['total']) for item in data]
    
#     # Aggregate by category for pie chart
#     category_data = expenses.values('category__name').annotate(total=Sum('amount')).filter(total__gt=0).order_by('-total')
#     category_labels = [item['category__name'] for item in category_data]
#     category_values = [float(item['total']) for item in category_data]
    
#     # Get months
#     import calendar
#     month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
#     context = {
#         'available_years': available_years,
#         'categories': categories,
#         'month_choices': month_choices,
#         'selected_year': selected_year,
#         'selected_month': selected_month,
#         'selected_category': selected_category,
#         'labels_json': json.dumps(labels),
#         'values_json': json.dumps(values),
#     }
#     return render(request, 'ledger/test.html', context)

def test_view(request):
    today = date.today()
    current_year = today.year
    current_month = today.month

    if request.method == "POST":
        selected_year = int(request.POST.get("year", current_year))
        selected_month = int(request.POST.get("month", current_month))
        selected_category = request.POST.get("category", "all")
    else:
        selected_year = current_year
        selected_month = current_month
        selected_category = "all"

    years_qs = Expense.objects.filter(user=request.user).dates("date", "year")
    available_years = sorted({d.year for d in years_qs} | {current_year}, reverse=True)

    expenses = Expense.objects.filter(
        user=request.user,
        date__year=selected_year,
        date__month=selected_month
    )

    category_ids = expenses.values_list("category_id", flat=True).distinct()
    categories = Category.objects.filter(id__in=category_ids)

    if selected_category != "all":
        expenses = expenses.filter(category_id=int(selected_category))

    subcat_data = expenses.values("subcategory__name").annotate(total=Sum("amount"))
    labels = [r["subcategory__name"] or "No Subcategory" for r in subcat_data]
    values = [float(r["total"]) for r in subcat_data]

    cat_data = expenses.values("category__name").annotate(total=Sum("amount"))
    cat_labels = [r["category__name"] or "Uncategorized" for r in cat_data]
    cat_values = [float(r["total"]) for r in cat_data]

    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        "available_years": available_years,
        "categories": categories,
        "month_choices": month_choices,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "selected_category": selected_category,

        # ✅ JSON STRINGS (VALID JS)
        "labels_json": json.dumps(labels),
        "values_json": json.dumps(values),
        "category_labels_json": json.dumps(cat_labels),
        "category_values_json": json.dumps(cat_values),
    }

    return render(request, "ledger/test.html", context)

def health(request):
    # Must be super lightweight; no DB, no cache misses, no auth
    return HttpResponse("ok", content_type="text/plain")

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def export_expenses_csv(request):
    """Export filtered expenses as CSV with columns: date, category, subcategory, amount, description.

    Accepts GET params: year, month, category (category id or 'all').
    """
    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
    except (TypeError, ValueError):
        year = today.year

    try:
        month = int(request.GET.get('month', today.month))
    except (TypeError, ValueError):
        month = today.month

    category = request.GET.get('category', 'all')

    qs = Expense.objects.filter(user=request.user, date__year=year, date__month=month).order_by('date')
    if category and category != 'all':
        try:
            cat_id = int(category)
            qs = qs.filter(category_id=cat_id)
        except ValueError:
            pass

    # Build CSV response
    filename = f"expenses_{request.user.id}_{year}_{month}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['date', 'category', 'subcategory', 'amount', 'description'])

    for e in qs:
        category_name = e.category.name if e.category else ''
        subcategory_name = e.subcategory.name if e.subcategory else ''
        writer.writerow([
            e.date.isoformat(),
            category_name,
            subcategory_name,
            str(e.amount),
            e.description or '',
        ])

    return response
    return response

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def keepalive(request):
    # Simply touch the session; Idle middleware will update last_activity
    # Return remaining time if you want to show a countdown
    return JsonResponse({"status": "ok"})

User = get_user_model()

@require_POST
@csrf_protect
def google_signin(request):
    """
    Verifies Google ID token, upserts a user by email, and logs them in via Django session.
    Expects JSON body: {"id_token": "<JWT>"}
    """
    logger.info("Google sign-in request received")
    
    # Parse JSON
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.debug("Request body parsed successfully")
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        return HttpResponseBadRequest("Invalid JSON")

    token = data.get("id_token")
    if not token:
        logger.warning("No id_token provided in request")
        return HttpResponseBadRequest("id_token missing")

    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    if not client_id:
        logger.error("GOOGLE_CLIENT_ID not configured in settings")
        return JsonResponse({"ok": False, "message": "Server misconfigured: GOOGLE_CLIENT_ID missing"}, status=500)
    
    logger.info(f"Google client ID configured: {client_id[:10]}...")

    try:
        # Verify signature & claims
        logger.info("Verifying Google ID token...")
        claims = id_token.verify_oauth2_token(
            token,
            grequests.Request(),
            client_id,
        )
        logger.info(f"Token verified successfully. Claims: {list(claims.keys())}")

        # Issuer check
        issuer = claims.get("iss")
        valid_issuers = ["accounts.google.com", "https://accounts.google.com"]
        if issuer not in valid_issuers:
            logger.warning(f"Invalid token issuer: {issuer}")
            return JsonResponse({"ok": False, "message": "Invalid token issuer"}, status=401)

        # Basic claims
        email = claims.get("email")
        email_verified = claims.get("email_verified", False)
        name = claims.get("name") or ""
        picture = claims.get("picture")
        sub = claims.get("sub")  # Stable Google user id as string

        logger.info(f"Token claims - email: {email}, email_verified: {email_verified}, name: {name}")

        if not email:
            logger.warning("Email missing from Google token")
            return JsonResponse({"ok": False, "message": "Email missing from Google token"}, status=400)
        if not email_verified:
            logger.warning(f"Email {email} not verified with Google")
            return JsonResponse({"ok": False, "message": "Email not verified with Google"}, status=403)

        # (Optional) Restrict to a domain:
        # hd = claims.get("hd")
        # if hd != "yourcompany.com":
        #     return JsonResponse({"ok": False, "message": "Domain not allowed"}, status=403)

        # Upsert user by email
        first_name = name.split(" ")[0] if name else ""
        last_name = " ".join(name.split(" ")[1:]) if name and len(name.split(" ")) > 1 else ""
        
        logger.info(f"Looking up or creating user with email: {email}")
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,  # Needed if you use default Django User with required username
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        
        if created:
            logger.info(f"New user created: {email}")
        else:
            logger.info(f"Existing user found: {email}")

        # Optionally update names if empty and Google provided them
        fields_to_update = []
        if not user.first_name and first_name:
            user.first_name = first_name
            fields_to_update.append("first_name")
        if not user.last_name and last_name:
            user.last_name = last_name
            fields_to_update.append("last_name")
        if fields_to_update:
            user.save(update_fields=fields_to_update)
            logger.debug(f"Updated user fields: {fields_to_update}")

        # If you want to persist Google sub / avatar, add a Profile model and store:
        # profile, _ = Profile.objects.get_or_create(user=user)
        # profile.google_sub = sub
        # profile.avatar_url = picture
        # profile.save()

        # Create Django session
        login(request, user)
        logger.info(f"User {email} logged in successfully via Google OAuth")

        # Frontend will redirect to dashboard on success
        return JsonResponse({"ok": True})
    except Exception as e:
        logger.error(f"Google sign-in failed: {type(e).__name__}: {e}", exc_info=True)
        return JsonResponse({"ok": False, "message": f"Invalid token: {str(e)}"}, status=401)