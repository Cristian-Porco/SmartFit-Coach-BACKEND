from rest_framework import serializers
from .models import DetailsAccount, Weight, BodyMeasurement, FoodItem, FoodPlanItem, FoodPlan, FoodPlanSection, GymItem, \
    GymPlan, GymPlanItem, GymPlanSection, GymPlanSetDetail, GymMediaUpload


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
        fields = '__all__'

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

class GymItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymItem
        fields = '__all__'

class GymPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymPlan
        fields = '__all__'

class GymPlanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymPlanItem
        fields = '__all__'

class GymPlanSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymPlanSection
        fields = '__all__'

class GymPlanSetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymPlanSetDetail
        fields = '__all__'

class GymMediaUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymMediaUpload
        fields = '__all__'