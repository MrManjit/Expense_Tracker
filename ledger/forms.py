
from django import forms
from .models import Expense, Category, Subcategory

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'subcategory', 'amount', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control-custom'}),
            'description': forms.TextInput(attrs={'placeholder': 'Optional description', 'class': 'form-control-custom'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01', 'min': '0'}),
            'category': forms.Select(attrs={'class': 'form-select-custom'}),
            'subcategory': forms.Select(attrs={'class': 'form-select-custom'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Show all global categories
            self.fields['category'].queryset = Category.objects.all()
            # Subcategory will be filtered based on selected category via JavaScript or initial value
            all_subcategories = Subcategory.objects.all().select_related('category')
            self.fields['subcategory'].queryset = all_subcategories
            
            # Create choices with just subcategory names (not full names with >)
            choices = [('', '---------')]
            self.subcategory_category_map = {}
            for subcategory in all_subcategories:
                choices.append((subcategory.id, subcategory.name))
                self.subcategory_category_map[subcategory.id] = subcategory.category_id
            self.fields['subcategory'].choices = choices
            
            # If editing an existing expense, filter subcategory by its category
            if self.instance and self.instance.pk and self.instance.category:
                self.fields['subcategory'].queryset = Subcategory.objects.filter(
                    category=self.instance.category
                )
    
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Category is required.")
        return category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-custom'}),
        }

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category', 'name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'category': forms.Select(attrs={'class': 'form-select-custom'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()