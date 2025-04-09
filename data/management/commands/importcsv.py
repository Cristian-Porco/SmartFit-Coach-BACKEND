import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from data.models import FoodItem

User = get_user_model()

class Command(BaseCommand):
    help = "Importa alimenti da un file CSV nella tabella FoodItem"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Percorso del file CSV')

    def handle(self, *args, **options):
        path = options['csv_path']
        count = 0
        errors = 0

        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    author = User.objects.get(id=row['author_id'])

                    item, created = FoodItem.objects.get_or_create(
                        name=row['name'].strip(),
                        barcode=row['barcode'].strip(),
                        defaults={
                            'brand': row['brand'].strip(),
                            'kcal_per_100g': float(row['kcal_per_100g']),
                            'protein_per_100g': float(row['protein_per_100g']),
                            'carbs_per_100g': float(row['carbs_per_100g']),
                            'sugars_per_100g': float(row['sugars_per_100g']),
                            'fats_per_100g': float(row['fats_per_100g']),
                            'saturated_fats_per_100g': float(row['saturated_fats_per_100g']),
                            'fiber_per_100g': float(row['fiber_per_100g']),
                            'author': author,
                        }
                    )
                    if created:
                        count += 1
                except Exception as e:
                    errors += 1
                    self.stderr.write(self.style.ERROR(f"Errore su '{row['name']}': {e}"))

        self.stdout.write(self.style.SUCCESS(f"Import completato: {count} elementi creati, {errors} errori."))