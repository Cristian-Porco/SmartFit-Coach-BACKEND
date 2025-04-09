from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class DetailsAccount(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    biological_gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    height_cm = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(300)])
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        default='profile_pics/default.jpg'
    )

    def __str__(self):
        return f"{self.author.first_name} {self.author.last_name} ({self.author.username})"


class Weight(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date_recorded = models.DateField()
    weight_value = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"[{self.id_user}] {self.weight_value}kg - {self.date_recorded}"


class BodyMeasurement(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Misure corporee in cm
    chest = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Torace
    bicep = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Bicipite
    thigh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Coscia
    waist = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Vita
    hips = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Fianchi
    abdomen = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Addome
    calf = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Polpaccio
    neck = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Collo
    shoulders = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Spalle

    # Data della misurazione
    date_recorded = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Misure per {self.user.username} - {self.date_recorded}"

    def average_measurement(self):
        # Calcola la media di alcune misure selezionate
        measures = [self.chest, self.bicep, self.thigh, self.waist, self.hips, self.abdomen, self.calf, self.neck,
                    self.shoulders]
        measures = [measure for measure in measures if measure is not None]
        if measures:
            return sum(measures) / len(measures)
        return None


class FoodItem(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=50, unique=True, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    kcal_per_100g = models.FloatField()
    protein_per_100g = models.FloatField()
    carbs_per_100g = models.FloatField()
    sugars_per_100g = models.FloatField(null=True, blank=True)
    fats_per_100g = models.FloatField()
    saturated_fats_per_100g = models.FloatField(null=True, blank=True)
    fiber_per_100g = models.FloatField()

    def __str__(self):
        if self.brand:
            return self.name + " (" + self.brand + ")"
        return self.name


class FoodPlan(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    food_items = models.ManyToManyField(FoodItem, through='FoodPlanItem')
    start_date = models.DateField()
    end_date = models.DateField()
    max_kcal = models.FloatField()
    max_protein = models.FloatField()
    max_carbs = models.FloatField()
    max_fats = models.FloatField()

    def __str__(self):
        return f"Food Plan {self.start_date} - {self.end_date}"

class FoodPlanSection(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    start_time = models.IntegerField()

    def __str__(self):
        return f"[{self.author}] {self.name} - ORARIO EVENTUALE: {self.start_time}"

class FoodPlanItem(models.Model):
    eaten = models.BooleanField(default=False)
    food_plan = models.ForeignKey(FoodPlan, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    food_section = models.ForeignKey(FoodPlanSection, on_delete=models.CASCADE)
    quantity_in_grams = models.FloatField()