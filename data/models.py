from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

from data.utils import infer_goal_target, explain_goal_target  # importa la funzione dalla fase 2

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

    goal_description = models.CharField(
        max_length=160,
        blank=True,
        default='',
        help_text="Descrivi brevemente il tuo obiettivo (max 160 caratteri)"
    )

    GOAL_CHOICES = [
        ('fitness', 'Fitness'),
        ('bodybuilding', 'Bodybuilding'),
        ('powerlifting', 'Powerlifting'),
        ('streetlifting', 'Streetlifting'),
    ]

    goal_targets = models.CharField(choices=GOAL_CHOICES, blank=True)

    # 🆕 Campo per spiegazione generata
    goal_targets_explanation = models.TextField(
        blank=True,
        help_text="Spiegazione generata dall'IA sul perché è stato selezionato questo obiettivo."
    )

    def save(self, *args, **kwargs):
        if self.goal_description:
            try:
                if self.pk:
                    previous = DetailsAccount.objects.get(pk=self.pk)
                    if previous.goal_description != self.goal_description:
                        inferred = infer_goal_target(self.goal_description)
                        if inferred in dict(self.GOAL_CHOICES):
                            self.goal_targets = inferred
                        self.goal_targets_explanation = explain_goal_target(self.goal_description, self.goal_targets)
                else:
                    inferred = infer_goal_target(self.goal_description)
                    if inferred in dict(self.GOAL_CHOICES):
                        self.goal_targets = inferred
                    self.goal_targets_explanation = explain_goal_target(self.goal_description, self.goal_targets)
            except Exception as e:
                print(f"Errore durante l'inferenza del goal: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.author.first_name} {self.author.last_name} ({self.author.username})"


class Weight(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date_recorded = models.DateField()
    weight_value = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"[{self.author}] {self.weight_value}kg - {self.date_recorded}"


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
        return f"Misure per {self.author.username} - {self.date_recorded}"

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
    barcode = models.CharField(max_length=50, null=True, blank=True)
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

class GymPlan(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True)

    def clean(self):
        super().clean()

        if self.start_date and self.start_date.weekday() != 0:
            raise ValidationError({'start_date': 'La data di inizio deve essere un lunedì.'})

        if self.end_date and self.end_date.weekday() != 6:
            raise ValidationError({'end_date': 'La data di fine deve essere una domenica.'})

        if self.start_date and self.end_date:
            delta_days = (self.end_date - self.start_date).days
            if delta_days != 6:
                raise ValidationError('La settimana deve durare esattamente 7 giorni, da lunedì a domenica.')

    def __str__(self):
        return f"[{self.author}] Scheda di allenamento da {self.start_date} a {self.end_date}"

class GymPlanSection(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    GIORNI_SETTIMANA = [
        ("lun", "Lunedì"),
        ("mar", "Martedì"),
        ("mer", "Mercoledì"),
        ("gio", "Giovedì"),
        ("ven", "Venerdì"),
        ("sab", "Sabato"),
        ("dom", "Domenica"),
    ]

    gym_plan = models.ForeignKey(GymPlan, on_delete=models.CASCADE, null=True)

    day = models.CharField(max_length=3, choices=GIORNI_SETTIMANA)
    type = models.CharField(max_length=100, help_text="Es. Push, Gambe, Full Body", blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.author}] Sezione della scheda di allenamento da {self.gym_plan.start_date} a {self.gym_plan.end_date} - GIORNO {self.day}"

class GymPlanSetDetail(models.Model):
    plan_item = models.ForeignKey('GymPlanItem', on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey('GymItem', on_delete=models.CASCADE, default=None)

    order = models.PositiveIntegerField(help_text="Ordine del set nella lista", default=0)
    set_number = models.PositiveIntegerField()

    prescribed_reps_1 = models.PositiveIntegerField(default=0)
    actual_reps_1 = models.PositiveIntegerField(blank=True, null=True, default=0)
    prescribed_reps_2 = models.PositiveIntegerField(default=0)
    actual_reps_2 = models.PositiveIntegerField(blank=True, null=True, default=0)

    rir = models.PositiveIntegerField(blank=True, null=True, help_text="Reps in reserve", default=0)
    rest_seconds = models.PositiveIntegerField(blank=True, null=True, default=60)
    weight = models.FloatField(blank=True, null=True, help_text="Peso in kg", default=0)
    tempo_fcr = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Formato: 'eccentrica-pausa-concentrica', es. '3-1-2'",
        default="0-0-0"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.exercise}] Ordine: {self.order} - Numero set: {self.set_number}"

    def delete(self, *args, **kwargs):
        plan_item = self.plan_item
        super().delete(*args, **kwargs)

        # Se non ci sono più set legati a questo plan_item, lo elimino
        if plan_item.sets.count() == 0:
            plan_item.delete()

class GymMediaUpload(models.Model):
    file = models.FileField(upload_to='gym_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class GymItem(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    FORCE_CHOICES = [
        ("pull", "Pull"),
        ("push", "Push"),
        ("static", "Statico"),
    ]

    LEVEL_CHOICES = [
        ("beginner", "Principiante"),
        ("intermediate", "Intermedio"),
        ("expert", "Esperto"),
    ]

    MECHANIC_CHOICES = [
        ("compound", "Multiarticolare"),
        ("isolation", "Isolamento"),
    ]

    CATEGORY_CHOICES = [
        ("cardio", "Cardio"),
        ("olympic weightlifting", "Olympic Weightlifting"),
        ("plyometrics", "Plyometrics"),
        ("powerlifting", "Powerlifting"),
        ("strength", "Strength"),
        ("stretching", "Stretching"),
        ("strongman", "Strongman"),
    ]

    EQUIPMENT_CHOICES = [
        ("bands", "Elastici"),
        ("barbell", "Bilanciere"),
        ("body only", "Corpo Libero"),
        ("cable", "Cavi"),
        ("dumbbell", "Manubri"),
        ("e-z curl bar", "Bilanciere E-Z"),
        ("exercise ball", "Palla Fitness"),
        ("foam roll", "Rullo di Schiuma"),
        ("kettlebells", "Kettlebell"),
        ("machine", "Macchinario"),
        ("medicine ball", "Palla Medica"),
        ("other", "Altro"),
    ]

    MUSCLE_CHOICES = [
        ("abdominals", "Addominali"),
        ("abductors", "Abduttori"),
        ("adductors", "Adduttori"),
        ("biceps", "Bicipiti"),
        ("calves", "Polpacci"),
        ("chest", "Petto"),
        ("forearms", "Avambracci"),
        ("glutes", "Glutei"),
        ("hamstrings", "Femorali"),
        ("lats", "Dorsali"),
        ("lower back", "Zona Lombare"),
        ("middle back", "Schiena Media"),
        ("neck", "Collo"),
        ("quadriceps", "Quadricipiti"),
        ("shoulders", "Spalle"),
        ("traps", "Trapezi"),
        ("triceps", "Tricipiti"),
    ]

    name = models.CharField(max_length=100)

    force = models.CharField(max_length=50, choices=FORCE_CHOICES, null=True, blank=True)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True)
    mechanic = models.CharField(max_length=50, choices=MECHANIC_CHOICES, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    equipment = models.CharField(max_length=50, choices=EQUIPMENT_CHOICES, null=True, blank=True)

    primary_muscle = models.CharField(max_length=50, choices=MUSCLE_CHOICES, null=True, blank=True)
    secondary_muscles = models.JSONField(default=list, blank=True)
    instructions = models.JSONField(default=list, blank=True)

    image_urls = models.ManyToManyField(GymMediaUpload)

    def __str__(self):
        return self.name

    def clean(self):
        # Validazione opzionale per muscoli validi
        invalid_secondary = [m for m in self.secondary_muscles if m not in self.MUSCLE_CHOICES]
        if invalid_secondary:
            raise ValidationError({
                "secondary_muscles": f"Valori non validi: {invalid_secondary}" if invalid_secondary else None
            })

class GymPlanItem(models.Model):
    section = models.ForeignKey('GymPlanSection', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class TechniqueType(models.TextChoices):
        NULL = 'null', 'Null'
        BILATERAL = 'bilateral', 'Bilaterale (entrambe gli arti)'
        UNILATERAL = 'unilateral', 'Unilaterale (singolo arto)'
        TEMPO_BASED = 'tempo-based', 'Tempo-Based (durata fissa)'
        DROP_SET = 'drop_set', 'Drop Set / Stripping'
        SUPER_SET = 'super_set', 'Super Set / Giant Set'
        FORCED_REPS = 'forced_reps', 'Serie Forzate'
        HALF_REPS = 'half_reps', 'Half Reps'
        REST_PAUSE = 'rest_pause', 'Rest-Pause'
        MYOREPS = 'myoreps', 'MyoReps'
        PRE_FATIGUE = 'pre_fatigue', 'Pre-Affaticamento'
        NEGATIVE = 'negative', 'Negativa Forzata'
        PEAK_CONTRACTION = 'peak_contraction', 'Contrazione di Picco'
        TEMPO = 'tempoTUT', 'Tempo Training / TUT'
        ISOMETRIC = 'isometric', 'Contrazioni Isometriche'
        SEVEN_SEVEN = 'seven_seven', '21 Serie / 7-7-7'
        CLUSTER = 'cluster', 'Cluster Set'
        PYRAMID = 'pyramid', 'Piramidale'
        WAVE_LOADING = 'wave_loading', 'Wave Loading'
        ISOMETRIC_OVERLOAD = 'isometric_overload', 'Isometric Overload'
        ACCOMODATING_RESISTANCE = 'accomodating', 'Accommodating Resistance'
        PAUSE_REPS = 'pause_reps', 'Pause Reps'
        EMOM = 'emom', 'EMOM'
        AMRAP = 'amrap', 'AMRAP'
        DEATH_SET = 'death_set', 'Death Set'

    intensity_techniques = models.JSONField(default=list, blank=True, help_text="Lista di tecniche d’intensità (es: ['drop_set', 'tempo'])")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.notes}"