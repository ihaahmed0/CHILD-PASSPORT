from django.core.management.base import BaseCommand
from children.models import AssessmentCategory


class Command(BaseCommand):
    help = 'Seed assessment categories'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Height & Weight', 'order': 1},
            {'name': 'Posture Screening', 'order': 2},
            {'name': 'Flexibility Test', 'order': 3},
            {'name': 'Range of Motion', 'order': 4},
        ]
        
        for cat_data in categories:
            category, created = AssessmentCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'order': cat_data['order']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )