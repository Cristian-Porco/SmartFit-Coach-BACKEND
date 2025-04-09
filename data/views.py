from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import (
    DetailsAccount, Weight, BodyMeasurement,
    FoodItem, FoodPlan, FoodPlanItem, FoodPlanSection
)
from .serializers import (
    DetailsAccountSerializer, WeightSerializer, BodyMeasurementSerializer,
    FoodItemSerializer, FoodPlanSerializer, FoodPlanItemSerializer, FoodPlanSectionSerializer
)


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
    user_field = 'id_user'


class WeightListView(UserQuerySetMixin, generics.ListAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'id_user'

    def get_queryset(self):
        return super().get_queryset().order_by('-date_recorded')


class WeightUpdateView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'id_user'


class WeightDeleteView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]
    user_field = 'id_user'


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