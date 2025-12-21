from django.core.management.base import BaseCommand
from ledger.models import Category, Subcategory

class Command(BaseCommand):
    help = 'Populate database with default global expense categories and subcategories'

    def handle(self, *args, **options):
        # Define categories and subcategories
        categories_data = {
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

        created_count = 0
        
        for main_category_name, subcategories in categories_data.items():
            # Create main category
            main_category, created = Category.objects.get_or_create(
                name=main_category_name,
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created main category: {main_category_name}')
            
            # Create subcategories
            for subcategory_name in subcategories:
                subcategory, created = Subcategory.objects.get_or_create(
                    category=main_category,
                    name=subcategory_name,
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created subcategory: {subcategory_name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} global categories and subcategories')
        )