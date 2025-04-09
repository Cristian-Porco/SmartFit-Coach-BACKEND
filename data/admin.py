from django.contrib import admin

from data.models import DetailsAccount, Weight, BodyMeasurement, FoodItem, FoodPlan, FoodPlanItem, FoodPlanSection, \
    GymItem, GymPlanItem, GymPlan, GymMediaUpload, GymPlanSection, GymPlanSetDetail

# Register your models here.
admin.site.register(DetailsAccount)

admin.site.register(Weight)

admin.site.register(BodyMeasurement)

admin.site.register(FoodItem)
admin.site.register(FoodPlan)
admin.site.register(FoodPlanItem)
admin.site.register(FoodPlanSection)

admin.site.register(GymItem)
admin.site.register(GymMediaUpload)
admin.site.register(GymPlan)
admin.site.register(GymPlanItem)
admin.site.register(GymPlanSection)
admin.site.register(GymPlanSetDetail)