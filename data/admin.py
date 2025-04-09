from django.contrib import admin

from data.models import DetailsAccount, Weight, BodyMeasurement, FoodItem, FoodPlan, FoodPlanItem, FoodPlanSection

# Register your models here.
admin.site.register(DetailsAccount)
admin.site.register(Weight)
admin.site.register(BodyMeasurement)
admin.site.register(FoodItem)
admin.site.register(FoodPlan)
admin.site.register(FoodPlanItem)
admin.site.register(FoodPlanSection)