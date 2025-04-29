from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

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


# ======== GYM ITEM ========
class GymItemListView(generics.ListAPIView):
    queryset = GymItem.objects.all()
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