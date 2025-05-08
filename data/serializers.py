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
                  'email', 'profile_picture', 'goal_description', 'goal_targets', 'goal_targets_explanation']

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
    force_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    mechanic_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    equipment_display = serializers.SerializerMethodField()
    primary_muscle_display = serializers.SerializerMethodField()

    class Meta:
        model = GymItem
        fields = [
            'id',
            'author',
            'name',
            'force', 'force_display',
            'level', 'level_display',
            'mechanic', 'mechanic_display',
            'category', 'category_display',
            'equipment', 'equipment_display',
            'primary_muscle', 'primary_muscle_display',
            'secondary_muscles',
            'instructions',
            'image_urls',
        ]

    def get_force_display(self, obj):
        return obj.get_force_display() if obj.force else None

    def get_level_display(self, obj):
        return obj.get_level_display() if obj.level else None

    def get_mechanic_display(self, obj):
        return obj.get_mechanic_display() if obj.mechanic else None

    def get_category_display(self, obj):
        return obj.get_category_display() if obj.category else None

    def get_equipment_display(self, obj):
        return obj.get_equipment_display() if obj.equipment else None

    def get_primary_muscle_display(self, obj):
        return obj.get_primary_muscle_display() if obj.primary_muscle else None

class GymPlanSerializer(serializers.ModelSerializer):
    gym_plan_items = serializers.SerializerMethodField()

    class Meta:
        model = GymPlan
        fields = '__all__'

    def get_gym_plan_items(self, obj):
        return GymPlanItemSerializer(
            GymPlanItem.objects.filter(section__gym_plan=obj),
            many=True
        ).data

class GymPlanSynthesizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymPlan
        fields = '__all__'

class GymPlanSectionSerializer(serializers.ModelSerializer):
    day_display = serializers.SerializerMethodField()

    class Meta:
        model = GymPlanSection
        fields = [
            'id',
            'author',
            'gym_plan',
            'day', 'day_display',
            'type',
            'note',
        ]

    def get_day_display(self, obj):
        return obj.get_day_display() if obj.day else None


class GymPlanSetDetailSerializer(serializers.ModelSerializer):
    # ID accettato in scrittura
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=GymItem.objects.all(),
        source='exercise',
        write_only=True
    )

    # Oggetto completo visibile in lettura
    exercise = GymItemSerializer(read_only=True)

    class Meta:
        model = GymPlanSetDetail
        fields = '__all__'

class GymMediaUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymMediaUpload
        fields = '__all__'

class GymPlanItemSerializer(serializers.ModelSerializer):
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=GymPlanSection.objects.all(),
        source='section',
        write_only=True
    )
    section = GymPlanSectionSerializer(read_only=True)
    sets = GymPlanSetDetailSerializer(many=True, read_only=True)
    intensity_techniques_display = serializers.SerializerMethodField()

    class Meta:
        model = GymPlanItem
        fields = [
            'id',
            'section',
            'section_id',
            'order',
            'sets',
            'notes',
            'intensity_techniques',
            'intensity_techniques_display',  # aggiunto campo leggibile
        ]

    def get_intensity_techniques_display(self, obj):
        if not obj.intensity_techniques:
            return []
        return [
            GymPlanItem.TechniqueType(tech).label
            for tech in obj.intensity_techniques
            if tech in GymPlanItem.TechniqueType.values
        ]
