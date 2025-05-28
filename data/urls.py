from django.urls import path

from .views import (
    DetailsAccountCreateView, DetailsAccountRetrieveUpdateView,
    WeightCreateView, WeightListView, WeightUpdateView, WeightDeleteView,
    BodyMeasurementListView, BodyMeasurementCreateView, BodyMeasurementUpdateView,
    BodyMeasurementDeleteView, BodyMeasurementRetrieveView,
    FoodItemListView, FoodItemListMeView, FoodItemRetrieveView,
    FoodItemCreateView, FoodItemUpdateView, FoodItemDeleteView,
    FoodPlanListView, FoodPlanRetrieveView, FoodPlanCreateView,
    FoodPlanUpdateView, FoodPlanDeleteView,
    FoodPlanItemRetrieveView, FoodPlanItemCreateView,
    FoodPlanItemUpdateView, FoodPlanItemDeleteView,
    FoodPlanSectionListView, FoodPlanSectionRetrieveView,
    FoodPlanSectionCreateView, FoodPlanSectionUpdateView,
    FoodPlanSectionDeleteView, GymItemListView, GymItemListMeView, GymItemRetrieveView, GymItemCreateView,
    GymItemUpdateView, GymItemDeleteView, GymMediaUploadRetrieveView, GymMediaUploadCreateView,
    GymMediaUploadUpdateView, GymMediaUploadDeleteView, GymPlanListView, GymPlanRetrieveView, GymPlanCreateView,
    GymPlanUpdateView, GymPlanDeleteView, GymPlanItemRetrieveView, GymPlanItemCreateView, GymPlanItemUpdateView,
    GymPlanItemDeleteView, GymPlanSectionListView, GymPlanSectionRetrieveView, GymPlanSectionCreateView,
    GymPlanSectionUpdateView, GymPlanSectionDeleteView, GymPlanSetDetailDeleteView, GymPlanSetDetailUpdateView,
    GymPlanSetDetailCreateView, GymPlanSetDetailRetrieveView, GymPlanSynthesizedListView, get_first_available_order,
    WeightAnalysisAIView, BodyMeasurementAnalysisView, FoodPlanParsingAIView, FoodImageParsingAIView,
    FoodPlanOptimizationAIView, FoodPlanGeneratePlanItemAIView, FoodPlanGenerateMacroAIView,
    FoodPlanGenerateAlternativeAIView, FoodPlanCloneView, GymPlanCloneView, GymPlanClassifyDectionAIView,
    GymPlanGenerateNoteAIView, GymPlanSectionGenerateNoteAIView, GymPlanItemGenerateNoteAIView,
    GymPlanGenerateEntirePlanAIView, GymPlanItemGenerateAlternativeAIView, GymPlanItemGenerateWarmupAIView,
    GymPlanSetDetailGenerateSuggestedWeightAIView
)

urlpatterns = [
    # Details Account
    path('detailsaccount/', DetailsAccountCreateView.as_view(), name='detailsaccount-create'),
    path('detailsaccount/me/', DetailsAccountRetrieveUpdateView.as_view(), name='detailsaccount-detail'),

    # Weight
    path('weight/me/', WeightListView.as_view(), name='weight-list'),
    path('weight/create/', WeightCreateView.as_view(), name='weight-create'),
    path('weight/update/<int:pk>/', WeightUpdateView.as_view(), name='weight-update'),
    path('weight/delete/<int:pk>/', WeightDeleteView.as_view(), name='weight-delete'),
    path("weight/analysis/", WeightAnalysisAIView.as_view(), name="weight-analysis"),

    # Body Measurements
    path('body-measurement/me/', BodyMeasurementListView.as_view(), name='body-list'),
    path('body-measurement/<int:pk>/', BodyMeasurementRetrieveView.as_view(), name='body-detail'),
    path('body-measurement/create/', BodyMeasurementCreateView.as_view(), name='body-create'),
    path('body-measurement/update/<int:pk>/', BodyMeasurementUpdateView.as_view(), name='body-update'),
    path('body-measurement/delete/<int:pk>/', BodyMeasurementDeleteView.as_view(), name='body-delete'),
    path("body-measurement/analysis/", BodyMeasurementAnalysisView.as_view(), name="body-analysis"),

    # Food Items
    path('food-item/', FoodItemListView.as_view(), name='fooditem-list'),
    path('food-item/me/', FoodItemListMeView.as_view(), name='fooditem-list-me'),
    path('food-item/<int:pk>/', FoodItemRetrieveView.as_view(), name='fooditem-detail'),
    path('food-item/create/', FoodItemCreateView.as_view(), name='fooditem-create'),
    path('food-item/update/<int:pk>/', FoodItemUpdateView.as_view(), name='fooditem-update'),
    path('food-item/delete/<int:pk>/', FoodItemDeleteView.as_view(), name='fooditem-delete'),

    # Food Plan
    path('food-plan/me/', FoodPlanListView.as_view(), name='foodplan-list'),
    path('food-plan/<int:pk>/', FoodPlanRetrieveView.as_view(), name='foodplan-detail'),
    path('food-plan/create/', FoodPlanCreateView.as_view(), name='foodplan-create'),
    path('food-plan/update/<int:pk>/', FoodPlanUpdateView.as_view(), name='foodplan-update'),
    path('food-plan/delete/<int:pk>/', FoodPlanDeleteView.as_view(), name='foodplan-delete'),
    path('food-plan/clone/<int:pk>/', FoodPlanCloneView, name='foodplan-clone'),
    path('food-plan/food-text-parsing/', FoodPlanParsingAIView.as_view(), name='foodplan-text-parsing'),
    path("food-plan/food-image-parsing/", FoodImageParsingAIView.as_view(), name='foodplan-image-parsing'),
    path("food-plan/optimize-grams/<int:plan_id>/", FoodPlanOptimizationAIView.as_view(), name="foodplan-optimize-grams"),
    path("food-plan/generate/<int:plan_id>/", FoodPlanGeneratePlanItemAIView.as_view(), name="foodplan-generate-plan-item"),
    path("food-plan/generate-macro/", FoodPlanGenerateMacroAIView.as_view(), name="foodplan-generate-macros"),
    path("food-plan/generate-alternative-section/", FoodPlanGenerateAlternativeAIView.as_view(), name="foodplan-generate-alternative-section"),

    # Food Plan Items
    path('food-plan-item/<int:pk>/', FoodPlanItemRetrieveView.as_view(), name='foodplanitem-detail'),
    path('food-plan-item/create/', FoodPlanItemCreateView.as_view(), name='foodplanitem-create'),
    path('food-plan-item/update/<int:pk>/', FoodPlanItemUpdateView.as_view(), name='foodplanitem-update'),
    path('food-plan-item/delete/<int:pk>/', FoodPlanItemDeleteView.as_view(), name='foodplanitem-delete'),

    # Food Plan Sections
    path('food-plan-section/me/', FoodPlanSectionListView.as_view(), name='foodplansection-list'),
    path('food-plan-section/<int:pk>/', FoodPlanSectionRetrieveView.as_view(), name='foodplansection-detail'),
    path('food-plan-section/create/', FoodPlanSectionCreateView.as_view(), name='foodplansection-create'),
    path('food-plan-section/update/<int:pk>/', FoodPlanSectionUpdateView.as_view(), name='foodplansection-update'),
    path('food-plan-section/delete/<int:pk>/', FoodPlanSectionDeleteView.as_view(), name='foodplansection-delete'),

    # Gym Item
    path('gym-item/', GymItemListView.as_view(), name='gymitem-list'),
    path('gym-item/me/', GymItemListMeView.as_view(), name='gymitem-list'),
    path('gym-item/<int:pk>/', GymItemRetrieveView.as_view(), name='gymitem-detail'),
    path('gym-item/create/', GymItemCreateView.as_view(), name='gymitem-create'),
    path('gym-item/update/<int:pk>/', GymItemUpdateView.as_view(), name='gymitem-update'),
    path('gym-item/delete/<int:pk>/', GymItemDeleteView.as_view(), name='gymitem-delete'),

    # Gym Plan
    path('gym-plan/me/', GymPlanListView.as_view(), name='gymplan-list'),
    path('gym-plan/me-min/', GymPlanSynthesizedListView.as_view(), name='gymplan-synthesized-list'),
    path('gym-plan/<int:pk>/', GymPlanRetrieveView.as_view(), name='gymplan-detail'),
    path('gym-plan/create/', GymPlanCreateView.as_view(), name='gymplan-create'),
    path('gym-plan/update/<int:pk>/', GymPlanUpdateView.as_view(), name='gymplan-update'),
    path('gym-plan/delete/<int:pk>/', GymPlanDeleteView.as_view(), name='gymplan-delete'),
    path('gym-plan/clone/<int:pk>/', GymPlanCloneView, name='gymplan-clone'),
    path('gym-plan/generate-note/<int:pk>/', GymPlanGenerateNoteAIView, name='gymplan-generate-note'),
    path('gym-plan/generate-entire/<int:pk>/', GymPlanGenerateEntirePlanAIView, name='gymplan-generate_entire'),

    # Gym Plan Items
    path('gym-plan-item/<int:pk>/', GymPlanItemRetrieveView.as_view(), name='gymplanitem-detail'),
    path('gym-plan-item/create/', GymPlanItemCreateView.as_view(), name='gymplanitem-create'),
    path('gym-plan-item/update/<int:pk>/', GymPlanItemUpdateView.as_view(), name='gymplanitem-update'),
    path('gym-plan-item/delete/<int:pk>/', GymPlanItemDeleteView.as_view(), name='gymplanitem-delete'),
    path('gym-plan-item/first-available-order/<int:section_id>/', get_first_available_order, name='first_available_order'),
    path('gym-plan-item/generate-note/<int:pk>/', GymPlanItemGenerateNoteAIView, name='gymplanitem-generate-note'),
    path('gym-plan-item/generate-alternative/<int:pk>/', GymPlanItemGenerateAlternativeAIView, name='gymplanitem-generate-alternative'),
    path('gym-plan-item/generate-warmup/<int:pk>/', GymPlanItemGenerateWarmupAIView, name='gymplanitem-generate-warmup'),

    # Gym Plan Sections
    path('gym-plan-section/me/', GymPlanSectionListView.as_view(), name='gymplansection-list'),
    path('gym-plan-section/<int:pk>/', GymPlanSectionRetrieveView.as_view(), name='gymplansection-detail'),
    path('gym-plan-section/create/', GymPlanSectionCreateView.as_view(), name='gymplansection-create'),
    path('gym-plan-section/update/<int:pk>/', GymPlanSectionUpdateView.as_view(), name='gymplansection-update'),
    path('gym-plan-section/delete/<int:pk>/', GymPlanSectionDeleteView.as_view(), name='gymplansection-delete'),
    path('gym-plan-section/classify/<int:pk>/', GymPlanClassifyDectionAIView, name='gymplansection-classify'),
    path('gym-plan-section/generate-note/<int:pk>/', GymPlanSectionGenerateNoteAIView, name='gymplansection-generate-note'),

    # Gym Plan Set Detail
    path('gym-plan-set/<int:pk>/', GymPlanSetDetailRetrieveView.as_view(), name='gymplanset-detail'),
    path('gym-plan-set/create/', GymPlanSetDetailCreateView.as_view(), name='gymplanset-create'),
    path('gym-plan-set/update/<int:pk>/', GymPlanSetDetailUpdateView.as_view(), name='gymplanset-update'),
    path('gym-plan-set/delete/<int:pk>/', GymPlanSetDetailDeleteView.as_view(), name='gymplanset-delete'),
    path('gym-plan-set/suggested-weight/<int:pk>/', GymPlanSetDetailGenerateSuggestedWeightAIView, name='gymplanset-suggested-weight'),

    # Gym Media Upload
    path('gym-media-upload/<int:pk>/', GymMediaUploadRetrieveView.as_view(), name='gymmediaupload-detail'),
    path('gym-media-upload/create/', GymMediaUploadCreateView.as_view(), name='gymmediaupload-create'),
    path('gym-media-upload/update/<int:pk>/', GymMediaUploadUpdateView.as_view(), name='gymmediaupload-update'),
    path('gym-media-upload/delete/<int:pk>/', GymMediaUploadDeleteView.as_view(), name='gymmediaupload-delete'),
]
