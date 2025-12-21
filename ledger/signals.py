from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

# Default categories and subcategories data
DEFAULT_CATEGORIES = {
    'Food & Dining': [
        'Groceries',
        'Restaurants',
        'Fast Food',
        'Coffee Shops',
        'Delivery',
    ],
    'Transportation': [
        'Fuel',
        'Public Transport',
        'Taxi/Rideshare',
        'Parking',
        'Car Maintenance',
        'Car Insurance',
    ],
    'Housing': [
        'Rent',
        'Mortgage',
        'Utilities',
        'Internet',
        'Home Insurance',
        'Repairs & Maintenance',
    ],
    'Health & Fitness': [
        'Doctor Visits',
        'Pharmacy',
        'Gym Membership',
        'Sports Equipment',
        'Health Insurance',
    ],
    'Entertainment': [
        'Movies',
        'Games',
        'Streaming Services',
        'Concerts',
        'Hobbies',
    ],
    'Shopping': [
        'Clothing',
        'Electronics',
        'Home Goods',
        'Books',
        'Personal Care',
    ],
    'Education': [
        'Tuition',
        'Books',
        'Online Courses',
        'School Supplies',
    ],
    'Travel': [
        'Flights',
        'Hotels',
        'Vacation',
        'Travel Insurance',
    ],
    'Bills & Utilities': [
        'Electricity',
        'Water',
        'Gas',
        'Phone',
        'Internet',
    ],
    'Personal Care': [
        'Haircut',
        'Cosmetics',
        'Clothing',
        'Toiletries',
    ],
    'Insurance': [
        'Health Insurance',
        'Car Insurance',
        'Home Insurance',
        'Life Insurance',
    ],
    'Savings & Investments': [
        'Emergency Fund',
        'Retirement',
        'Investments',
    ],
    'Gifts & Donations': [
        'Gifts',
        'Charity',
        'Donations',
    ],
    'Other': [
        'Miscellaneous',
        'Unexpected Expenses',
    ],
}

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    """
    Create default global categories and subcategories after migrations
    """
    # Only run for the ledger app
    if sender.name == 'ledger':
        Category = apps.get_model('ledger', 'Category')
        Subcategory = apps.get_model('ledger', 'Subcategory')
        
        # Check if categories already exist
        if Category.objects.exists():
            return
        
        # Create default categories and subcategories
        for main_category_name, subcategories in DEFAULT_CATEGORIES.items():
            # Create main category
            main_category = Category.objects.create(
                name=main_category_name,
            )

            # Create subcategories
            for subcategory_name in subcategories:
                Subcategory.objects.create(
                    category=main_category,
                    name=subcategory_name,
                )