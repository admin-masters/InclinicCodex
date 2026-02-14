from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.PublisherLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("", views.publisher_dashboard, name="publisher_dashboard"),
    path("publisher/campaign/add/", views.campaign_add, name="campaign_add"),
    path("publisher/campaign/result/", views.campaign_create_result, name="campaign_create_result"),
    path("publisher/campaigns/", views.campaign_list, name="campaign_list"),
    path("publisher/campaign/<uuid:campaign_uuid>/inclinic/", views.inclinic_landing, name="inclinic_landing"),
    path("publisher/campaign/<uuid:campaign_uuid>/inclinic/configure/", views.inclinic_configure, name="inclinic_configure"),
    path("publisher/campaign/<uuid:campaign_uuid>/details/", views.campaign_details, name="campaign_details"),
    path("publisher/collaterals/", views.collateral_dashboard, name="collateral_dashboard"),
    path("publisher/campaign/<uuid:campaign_uuid>/collaterals/add/", views.collateral_add, name="collateral_add"),
    path("publisher/collaterals/<int:collateral_id>/edit/", views.collateral_edit, name="collateral_edit"),
    path("publisher/collaterals/<int:collateral_id>/delete/", views.collateral_delete, name="collateral_delete"),
    path("publisher/collaterals/<int:collateral_id>/preview/", views.collateral_preview, name="collateral_preview"),
]

handler403 = "core.views.forbidden_view"
