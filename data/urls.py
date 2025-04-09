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
    FoodPlanSectionDeleteView
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

    # Body Measurements
    path('body-measurement/me/', BodyMeasurementListView.as_view(), name='body-list'),
    path('body-measurement/<int:pk>/', BodyMeasurementRetrieveView.as_view(), name='body-detail'),
    path('body-measurement/create/', BodyMeasurementCreateView.as_view(), name='body-create'),
    path('body-measurement/update/<int:pk>/', BodyMeasurementUpdateView.as_view(), name='body-update'),
    path('body-measurement/delete/<int:pk>/', BodyMeasurementDeleteView.as_view(), name='body-delete'),

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
]
