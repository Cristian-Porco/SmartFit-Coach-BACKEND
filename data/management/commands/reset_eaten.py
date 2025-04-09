from django.core.management.base import BaseCommand
from django.db import models
from data.models import FoodPlan, FoodPlanItem

# Questo comando custom Django viene eseguito per resettare il campo "eaten" a False
# in tutti i record di FoodPlanItem che appartengono a un FoodPlan in cui
# start_date è diverso da end_date. Questo serve per evitare che gli item
# risultino "mangiati" nei giorni successivi se il piano alimentare copre più giorni.

# COMMANDI DA INVIARE
# crontab -e
# 0 0 * * * /path/to/venv/bin/python /path/to/project/manage.py reset_eaten

class Command(BaseCommand):
    help = 'Resetta "eaten" a False per i FoodPlanItem i cui FoodPlan hanno start_date != end_date'

    def handle(self, *args, **kwargs):
        # Filtra gli ID dei FoodPlan con start_date diverso da end_date
        plan_ids = FoodPlan.objects.filter(
            start_date__isnull=False,
            end_date__isnull=False
        ).exclude(
            start_date=models.F('end_date')
        ).values_list('id', flat=True)

        # Reset "eaten" a False nei FoodPlanItem collegati a quei piani
        updated_count = FoodPlanItem.objects.filter(
            food_plan_id__in=plan_ids
        ).update(eaten=False)

        self.stdout.write(self.style.SUCCESS(
            f'Resettati {updated_count} FoodPlanItem con eaten=False.'
        ))
