import json

from rest_framework import generics
from rest_framework.decorators import api_view
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
    find_matching_food_items, select_best_food_item


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

                enriched.append({
                    "meal": meal_name,
                    "keywords": keywords,
                    "quantity": quantity,
                    "matched_food_item": best_match
                })

            return Response({"meals": enriched})

        except json.JSONDecodeError:
            return Response({"error": "Risposta non in formato JSON valido."}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


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