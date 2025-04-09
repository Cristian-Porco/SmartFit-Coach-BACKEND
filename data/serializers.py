from rest_framework import serializers
from .models import DetailsAccount, Weight, BodyMeasurement, FoodItem, FoodPlanItem, FoodPlan, FoodPlanSection


class DetailsAccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name', read_only=True)
    last_name = serializers.CharField(source='author.last_name', read_only=True)
    email = serializers.CharField(source='author.email', read_only=True)

    class Meta:
        model = DetailsAccount
        fields = ['author', 'username', 'first_name', 'last_name', 'date_of_birth', 'biological_gender', 'height_cm',
                  'email', 'profile_picture']

class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weight
        fields = ['id', 'id_user', 'date_recorded', 'weight_value']

class BodyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyMeasurement
        fields = '__all__'  # Include tutti i campi del modello, puoi modificare se desideri solo alcuni campi specifici

    average_measurement = serializers.SerializerMethodField()

    def get_average_measurement(self, obj):
        return obj.average_measurement()


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'


class FoodPlanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodPlanItem
        fields = '__all__'


class FoodPlanSerializer(serializers.ModelSerializer):
    food_items = FoodPlanItemSerializer(many=True, read_only=True, source='foodplanitem_set')

    class Meta:
        model = FoodPlan
        fields = '__all__'


class FoodPlanSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodPlanSection
        fields = '__all__'