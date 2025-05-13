import json
from datetime import timedelta

from django.db.models import ExpressionWrapper, F, FloatField, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from .models import (
    DetailsAccount, Weight, BodyMeasurement,
    FoodItem, FoodPlan, FoodPlanItem, FoodPlanSection, GymItem, GymMediaUpload, GymPlan, GymPlanItem, GymPlanSection,
    GymPlanSetDetail
)
from .serializers import (
    DetailsAccountSerializer, WeightSerializer, BodyMeasurementSerializer,
    FoodItemSerializer, FoodPlanSerializer, FoodPlanItemSerializer, FoodPlanSectionSerializer, GymItemSerializer,
    GymMediaUploadSerializer, GymPlanSerializer, GymPlanItemSerializer, GymPlanSectionSerializer,
    GymPlanSetDetailSerializer, GymPlanSynthesizedSerializer
)
from data.utils import generate_weight_analysis, generate_body_analysis, generate_food_analysis, \
    find_matching_food_items, select_best_food_item, generate_food_analysis_from_image_file, \
    generate_foodplan_adjustment, apply_foodplan_adjustment, generate_food_plan_from_context, generate_food_item, \
    generate_new_macros, generate_alternative_meals


# ======== MIXINS PER OTTIMIZZARE ========
class UserQuerySetMixin:
    user_field = 'author'

    def get_queryset(self):
        return self.queryset.filter(**{self.user_field: self.request.user})

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])


class UserCreateMixin:
    user_field = 'author'

    def perform_create(self, serializer):
        serializer.save(**{self.user_field: self.request.user})


# ======== DETAILS ACCOUNT ========
class DetailsAccountCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = DetailsAccount.objects.all()
    serializer_class = DetailsAccountSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if DetailsAccount.objects.filter(author=self.request.user).exists():
            raise ValidationError("Un utente può avere un solo DetailsAccount.")
        super().perform_create(serializer)


class DetailsAccountRetrieveUpdateView(UserQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = DetailsAccount.objects.all()
    serializer_class = DetailsAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.get(author=self.request.user)


# ======== WEIGHT ========
class WeightCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]


class WeightListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().order_by('-date_recorded')


class WeightAnalysisAIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            details = DetailsAccount.objects.get(author=user)
        except DetailsAccount.DoesNotExist:
            return Response({"error": "Profilo non trovato"}, status=404)

        weight_data = Weight.objects.filter(author=user).order_by("date_recorded")
        weights = [(w.date_recorded.strftime("%Y-%m-%d"), w.weight_value) for w in weight_data]

        if not weights:
            return Response({"error": "Nessun dato di peso registrato"}, status=400)

        analysis = generate_weight_analysis(weights, details.goal_targets)

        return Response({"analysis": analysis})


class WeightUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]


class WeightDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]


# ======== BODY MEASUREMENTS ========
class BodyMeasurementListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = BodyMeasurement.objects.all()
    serializer_class = BodyMeasurementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().order_by('-date_recorded')


class BodyMeasurementCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = BodyMeasurement.objects.all()
    serializer_class = BodyMeasurementSerializer
    permission_classes = [IsAuthenticated]


class BodyMeasurementRetrieveView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = BodyMeasurement.objects.all()
    serializer_class = BodyMeasurementSerializer
    permission_classes = [IsAuthenticated]


class BodyMeasurementUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = BodyMeasurement.objects.all()
    serializer_class = BodyMeasurementSerializer
    permission_classes = [IsAuthenticated]


class BodyMeasurementDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = BodyMeasurement.objects.all()
    serializer_class = BodyMeasurementSerializer
    permission_classes = [IsAuthenticated]


class BodyMeasurementAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = DetailsAccount.objects.get(author=user)
        except DetailsAccount.DoesNotExist:
            return Response({"error": "Profilo non trovato"}, status=404)

        qs = BodyMeasurement.objects.filter(author=user).order_by("date_recorded")
        if not qs.exists():
            return Response({"error": "Nessuna misurazione registrata"}, status=400)

        data = []
        for obj in qs:
            data.append({
                "date": obj.date_recorded.strftime("%Y-%m-%d"),
                "chest": float(obj.chest) if obj.chest else None,
                "bicep": float(obj.bicep) if obj.bicep else None,
                "thigh": float(obj.thigh) if obj.thigh else None,
                "waist": float(obj.waist) if obj.waist else None,
                "hips": float(obj.hips) if obj.hips else None,
                "abdomen": float(obj.abdomen) if obj.abdomen else None,
                "calf": float(obj.calf) if obj.calf else None,
                "neck": float(obj.neck) if obj.neck else None,
                "shoulders": float(obj.shoulders) if obj.shoulders else None,
            })

        analysis = generate_body_analysis(data, profile.goal_targets)
        return Response({"analysis": analysis})



# ======== FOOD ITEM ========
class FoodItemListView(generics.ListAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]


class FoodItemListMeView(UserQuerySetMixin, generics.ListAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]


class FoodItemRetrieveView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]


class FoodItemCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]


class FoodItemUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]


class FoodItemDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]


# ======== FOOD PLAN ========
class FoodPlanListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = FoodPlan.objects.all()
    serializer_class = FoodPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().order_by('-start_date')


class FoodPlanRetrieveView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = FoodPlan.objects.all()
    serializer_class = FoodPlanSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = FoodPlan.objects.all()
    serializer_class = FoodPlanSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = FoodPlan.objects.all()
    serializer_class = FoodPlanSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = FoodPlan.objects.all()
    serializer_class = FoodPlanSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanParsingAIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        sentence = request.data.get("sentence")

        if not sentence:
            return Response({"error": "Il campo 'sentence' è obbligatorio."}, status=400)

        try:
            meals = generate_food_analysis(sentence)
            enriched = []

            for meal in meals:
                meal_name = meal.get("meal")
                keywords = meal.get("keywords", [])
                quantity = meal.get("quantity")

                candidates = find_matching_food_items(keywords)
                best_match = select_best_food_item(meal_name, candidates)

                if best_match["id"]:
                    food_item = FoodItem.objects.get(id=best_match["id"])
                else:
                    food_item = generate_food_item(meal_name, user)
                    if not food_item:
                        continue

                enriched.append({
                    "meal": meal_name,
                    "keywords": keywords,
                    "quantity": quantity,
                    "matched_food_item": {
                        "id": food_item.id,
                        "name": food_item.name
                    }
                })

            return Response({"meals": enriched})

        except json.JSONDecodeError:
            return Response({"error": "Risposta non in formato JSON valido."}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class FoodImageParsingAIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user

        if "image" not in request.FILES:
            return Response({"error": "Il campo 'image' è obbligatorio."}, status=400)

        image = request.FILES["image"]

        try:
            meals = generate_food_analysis_from_image_file(image)
            enriched = []

            for meal in meals:
                meal_name = meal.get("meal")
                keywords = meal.get("keywords", [])
                quantity = meal.get("quantity")

                candidates = find_matching_food_items(keywords)
                best_match = select_best_food_item(meal_name, candidates)

                if best_match["id"]:
                    food_item = FoodItem.objects.get(id=best_match["id"])
                else:
                    food_item = generate_food_item(meal_name, user)
                    if not food_item:
                        continue

                enriched.append({
                    "meal": meal_name,
                    "keywords": keywords,
                    "quantity": quantity,
                    "matched_food_item": {
                        "id": food_item.id,
                        "name": food_item.name
                    }
                })

            return Response({"meals": enriched})

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class FoodPlanOptimizationAIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plan_id):
        try:
            food_plan = FoodPlan.objects.get(id=plan_id, author=request.user)

            result_json_str = generate_foodplan_adjustment(food_plan)

            if "Errore" in result_json_str:
                return Response({"error": "Errore nella generazione dell'ottimizzazione"}, status=500)

            result_data = json.loads(result_json_str)

            updated_ids = apply_foodplan_adjustment(result_data)

            updated_items = food_plan.foodplanitem_set.filter(id__in=updated_ids).values(
                "id", "quantity_in_grams", "food_item__name"
            )

            return Response({
                "success": True,
                "updated_count": len(updated_ids),
                "updated_items": list(updated_items)
            })

        except FoodPlan.DoesNotExist:
            return Response({"error": "Piano alimentare non trovato"}, status=404)
        except json.JSONDecodeError:
            return Response({"error": "Il modello ha restituito un JSON non valido."}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)



DEFAULT_SECTION_TIMES = {
    "colazione": 8,
    "spuntino": 10,
    "pranzo": 13,
    "merenda": 16,
    "cena": 20,
    "pre nanna": 22
}

def get_or_create_section(section_name: str, section_keywords: list, user, existing_sections: list) -> FoodPlanSection:
    def normalize(text): return text.strip().lower()
    normalized_name = normalize(section_name)
    keyword_set = set(normalize(k) for k in section_keywords + [normalized_name])

    for s in existing_sections:
        if normalize(s.name) in keyword_set:
            return s
        expected_time = DEFAULT_SECTION_TIMES.get(normalized_name)
        if expected_time and abs(s.start_time - expected_time) <= 1:
            return s

    start_time = DEFAULT_SECTION_TIMES.get(normalized_name, 12)
    new_section = FoodPlanSection.objects.create(
        author=user,
        name=section_name.strip().capitalize(),
        start_time=start_time
    )
    existing_sections.append(new_section)
    return new_section

class FoodPlanGeneratePlanItemAIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plan_id):
        user = request.user

        try:
            food_plan = FoodPlan.objects.get(id=plan_id, author=user)
        except FoodPlan.DoesNotExist:
            return Response({"error": "Piano alimentare non trovato"}, status=404)

        try:
            details = DetailsAccount.objects.get(author=user)
        except DetailsAccount.DoesNotExist:
            return Response({"error": "Profilo utente non trovato"}, status=404)

        # Dati ultimi 30 giorni
        today = timezone.now().date()
        last_month = today - timedelta(days=30)

        weights = Weight.objects.filter(author=user, date_recorded__gte=last_month)
        weights_data = [(w.date_recorded.strftime("%Y-%m-%d"), w.weight_value) for w in weights]

        measurements = BodyMeasurement.objects.filter(author=user, date_recorded__gte=last_month)
        measurements_data = []
        for m in measurements:
            row = {"date": m.date_recorded.strftime("%Y-%m-%d")}
            for f in ["chest", "waist", "hips", "arm", "leg"]:
                value = getattr(m, f, None)
                if value is not None:
                    row[f] = value
            measurements_data.append(row)

        # Macro attuali del piano
        prev_macros = {
            "max_protein": round(food_plan.max_protein),
            "max_carbs": round(food_plan.max_carbs),
            "max_fats": round(food_plan.max_fats),
            "max_kcal": round(food_plan.max_kcal)
        }

        # ⚙️ Chiamata AI
        ai_meals = generate_food_plan_from_context(
            details.goal_targets,
            weights_data,
            measurements_data,
            prev_macros
        )

        if not ai_meals:
            return Response({"error": "Piano non generato"}, status=500)

        # 🔁 Applica piano
        # Rimuove eventuali item esistenti
        FoodPlanItem.objects.filter(food_plan=food_plan).delete()
        sections = list(FoodPlanSection.objects.filter(author=user))

        created_items = []

        for meal in ai_meals:
            meal_name = meal["meal"]
            keywords = meal.get("keywords", [])
            quantity = meal["quantity"]
            section_name = meal.get("section", "")
            section_keywords = meal.get("section_keywords", [])

            # Sezione
            section = get_or_create_section(section_name, section_keywords, user, sections)

            # Alimento
            candidates = find_matching_food_items(keywords)
            best_match = select_best_food_item(meal_name, candidates)

            if best_match["id"]:
                food_item = FoodItem.objects.get(id=best_match["id"])
            else:
                food_item = generate_food_item(meal_name, user)
                if not food_item:
                    continue

            # Item
            FoodPlanItem.objects.create(
                eaten=False,
                food_plan=food_plan,
                food_item=food_item,
                food_section=section,
                quantity_in_grams=quantity
            )

            created_items.append({
                "meal": meal_name,
                "food_item": food_item.name,
                "quantity": quantity,
                "section": section.name
            })

        return Response({
            "message": "Piano generato con successo",
            "created_items": created_items
        })


class FoodPlanGenerateMacroAIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # === Carica obiettivo utente
        try:
            details = DetailsAccount.objects.get(author=user)
            goal = details.goal_targets
        except DetailsAccount.DoesNotExist:
            return Response({"error": "Profilo non trovato."}, status=404)

        today = timezone.now().date()
        start_date = today - timedelta(days=30)

        # === Peso
        weights = Weight.objects.filter(author=user, date_recorded__gte=start_date).order_by("date_recorded")
        weights_data = [(w.date_recorded.strftime("%Y-%m-%d"), w.weight_value) for w in weights]

        # === Misure corporee
        measurements = BodyMeasurement.objects.filter(author=user, date_recorded__gte=start_date).order_by("date_recorded")
        measurements_data = []
        for m in measurements:
            row = {"date": m.date_recorded.strftime("%Y-%m-%d")}
            for field in ["chest", "waist", "hips", "arm", "leg"]:  # adatta ai tuoi campi
                value = getattr(m, field, None)
                if value is not None:
                    row[field] = value
            measurements_data.append(row)

        # === Recupera piano alimentare più recente (prima di oggi)
        last_plan = (
            FoodPlan.objects.filter(author=user, start_date__lt=today)
            .order_by("-start_date")
            .first()
        )

        if not last_plan:
            return Response({"error": "Nessuna scheda alimentare precedente trovata."}, status=400)

        # === Calcolo macro totali dalla scheda
        # Formula: macro = valore_per_100g * (quantity_in_grams / 100)

        def macro_expr(field):
            return ExpressionWrapper(
                F(f"food_item__{field}") * F("quantity_in_grams") / 100,
                output_field=FloatField()
            )

        totals = FoodPlanItem.objects.filter(food_plan=last_plan).aggregate(
            max_protein=Sum(macro_expr("protein_per_100g")),
            max_carbs=Sum(macro_expr("carbs_per_100g")),
            max_fats=Sum(macro_expr("fats_per_100g"))
        )

        if not all(totals.values()):
            return Response({"error": "Macro incompleti nella scheda alimentare precedente."}, status=400)

        # Arrotonda i macro
        prev_macros = {
            "max_protein": round(totals["max_protein"]),
            "max_carbs": round(totals["max_carbs"]),
            "max_fats": round(totals["max_fats"])
        }

        # === Invoca AI
        result = generate_new_macros(
            goal=goal,
            weights=weights_data,
            measurements=measurements_data,
            prev_macros=prev_macros
        )

        return Response(result)

class FoodPlanGenerateAlternativeAIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        food_plan_id = request.data.get("food_plan_id")
        section_id = request.data.get("section_id")

        if not food_plan_id or not section_id:
            return Response({"error": "I campi 'food_plan_id' e 'section_id' sono obbligatori."}, status=400)

        try:
            food_plan = FoodPlan.objects.get(id=food_plan_id, author=user)
            section = FoodPlanSection.objects.get(id=section_id, author=user)
        except (FoodPlan.DoesNotExist, FoodPlanSection.DoesNotExist):
            return Response({"error": "FoodPlan o sezione non trovati"}, status=404)

        try:
            alternatives = generate_alternative_meals(section, user)
            if not alternatives:
                return Response({"error": "Nessuna alternativa generata"}, status=400)
            selected = alternatives[0]
        except Exception as e:
            return Response({"error": f"Errore generazione alternativa: {str(e)}"}, status=500)

        FoodPlanItem.objects.filter(food_plan=food_plan, food_section=section).delete()

        created_items = []
        for item in selected:
            try:
                food_item = FoodItem.objects.get(id=item["food_item_id"])
            except FoodItem.DoesNotExist:
                continue

            FoodPlanItem.objects.create(
                eaten=False,
                food_plan=food_plan,
                food_item=food_item,
                food_section=section,
                quantity_in_grams=item["quantity"]
            )

            created_items.append({
                "meal": item["meal"],
                "food_item": food_item.name,
                "quantity": item["quantity"]
            })

        return Response({
            "message": "Alternativa generata e applicata con successo",
            "created_items": created_items
        }, status=status.HTTP_201_CREATED)



# ======== FOOD PLAN ITEM ========
class FoodPlanItemRetrieveView(generics.RetrieveAPIView):
    queryset = FoodPlanItem.objects.all()
    serializer_class = FoodPlanItemSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanItemCreateView(generics.CreateAPIView):
    queryset = FoodPlanItem.objects.all()
    serializer_class = FoodPlanItemSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanItemUpdateView(generics.UpdateAPIView):
    queryset = FoodPlanItem.objects.all()
    serializer_class = FoodPlanItemSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanItemDeleteView(generics.DestroyAPIView):
    queryset = FoodPlanItem.objects.all()
    serializer_class = FoodPlanItemSerializer
    permission_classes = [IsAuthenticated]


# ======== FOOD PLAN SECTION ========
class FoodPlanSectionListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = FoodPlanSection.objects.all()
    serializer_class = FoodPlanSectionSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanSectionRetrieveView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = FoodPlanSection.objects.all()
    serializer_class = FoodPlanSectionSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanSectionCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = FoodPlanSection.objects.all()
    serializer_class = FoodPlanSectionSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanSectionUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = FoodPlanSection.objects.all()
    serializer_class = FoodPlanSectionSerializer
    permission_classes = [IsAuthenticated]


class FoodPlanSectionDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = FoodPlanSection.objects.all()
    serializer_class = FoodPlanSectionSerializer
    permission_classes = [IsAuthenticated]


# ======== GYM ITEM ========
class GymItemListView(generics.ListAPIView):
    queryset = GymItem.objects.all().order_by('name')
    serializer_class = GymItemSerializer
    permission_classes = [IsAuthenticated]

class GymItemListMeView(UserQuerySetMixin, generics.ListAPIView):
    queryset = GymItem.objects.all()
    serializer_class = GymItemSerializer
    permission_classes = [IsAuthenticated]

class GymItemRetrieveView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = GymItem.objects.all()
    serializer_class = GymItemSerializer
    permission_classes = [IsAuthenticated]

class GymItemCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = GymItem.objects.all()
    serializer_class = GymItemSerializer
    permission_classes = [IsAuthenticated]

class GymItemUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = GymItem.objects.all()
    serializer_class = GymItemSerializer
    permission_classes = [IsAuthenticated]

class GymItemDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = GymItem.objects.all()
    serializer_class = GymItemSerializer
    permission_classes = [IsAuthenticated]


# ======== GYM MEDIA UPLOAD ========
class GymMediaUploadRetrieveView(generics.RetrieveAPIView):
    queryset = GymMediaUpload.objects.all()
    serializer_class = GymMediaUploadSerializer
    permission_classes = [IsAuthenticated]

class GymMediaUploadCreateView(generics.CreateAPIView):
    queryset = GymMediaUpload.objects.all()
    serializer_class = GymMediaUploadSerializer
    permission_classes = [IsAuthenticated]

class GymMediaUploadUpdateView(generics.UpdateAPIView):
    queryset = GymMediaUpload.objects.all()
    serializer_class = GymMediaUploadSerializer
    permission_classes = [IsAuthenticated]

class GymMediaUploadDeleteView(generics.DestroyAPIView):
    queryset = GymMediaUpload.objects.all()
    serializer_class = GymMediaUploadSerializer
    permission_classes = [IsAuthenticated]


# ======== GYM PLAN ========
class GymPlanListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = GymPlan.objects.all()
    serializer_class = GymPlanSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSynthesizedListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = GymPlan.objects.all().order_by('-start_date')
    serializer_class = GymPlanSynthesizedSerializer
    permission_classes = [IsAuthenticated]

class GymPlanRetrieveView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = GymPlan.objects.all()
    serializer_class = GymPlanSerializer
    permission_classes = [IsAuthenticated]

class GymPlanCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = GymPlan.objects.all()
    serializer_class = GymPlanSerializer
    permission_classes = [IsAuthenticated]

class GymPlanUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = GymPlan.objects.all()
    serializer_class = GymPlanSerializer
    permission_classes = [IsAuthenticated]

class GymPlanDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = GymPlan.objects.all()
    serializer_class = GymPlanSerializer
    permission_classes = [IsAuthenticated]


# ======== GYM PLAN ITEM ========
class GymPlanItemRetrieveView(generics.RetrieveAPIView):
    queryset = GymPlanItem.objects.all()
    serializer_class = GymPlanItemSerializer
    permission_classes = [IsAuthenticated]

class GymPlanItemCreateView(generics.CreateAPIView):
    queryset = GymPlanItem.objects.all()
    serializer_class = GymPlanItemSerializer
    permission_classes = [IsAuthenticated]

class GymPlanItemUpdateView(generics.UpdateAPIView):
    queryset = GymPlanItem.objects.all()
    serializer_class = GymPlanItemSerializer
    permission_classes = [IsAuthenticated]

class GymPlanItemDeleteView(generics.DestroyAPIView):
    queryset = GymPlanItem.objects.all()
    serializer_class = GymPlanItemSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
def get_first_available_order(request, section_id):
    """
    Restituisce il primo valore libero per il campo 'order' all'interno di una sezione specifica.
    """
    used_orders = GymPlanItem.objects.filter(section_id=section_id).values_list('order', flat=True)
    used_set = set(used_orders)

    i = 0
    while i in used_set:
        i += 1

    return Response({'first_available_order': i})


# ======== GYM PLAN SECTION ========
class GymPlanSectionListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = GymPlanSection.objects.all()
    serializer_class = GymPlanSectionSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSectionRetrieveView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = GymPlanSection.objects.all()
    serializer_class = GymPlanSectionSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSectionCreateView(UserCreateMixin, generics.CreateAPIView):
    queryset = GymPlanSection.objects.all()
    serializer_class = GymPlanSectionSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSectionUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = GymPlanSection.objects.all()
    serializer_class = GymPlanSectionSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSectionDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = GymPlanSection.objects.all()
    serializer_class = GymPlanSectionSerializer
    permission_classes = [IsAuthenticated]


# ======== GYM PLAN SET DETAIL ========
class GymPlanSetDetailRetrieveView(generics.RetrieveAPIView):
    queryset = GymPlanSetDetail.objects.all()
    serializer_class = GymPlanSetDetailSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSetDetailCreateView(generics.CreateAPIView):
    queryset = GymPlanSetDetail.objects.all()
    serializer_class = GymPlanSetDetailSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSetDetailUpdateView(generics.UpdateAPIView):
    queryset = GymPlanSetDetail.objects.all()
    serializer_class = GymPlanSetDetailSerializer
    permission_classes = [IsAuthenticated]

class GymPlanSetDetailDeleteView(generics.DestroyAPIView):
    queryset = GymPlanSetDetail.objects.all()
    serializer_class = GymPlanSetDetailSerializer
    permission_classes = [IsAuthenticated]