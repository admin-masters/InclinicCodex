from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('publisher/campaign/new/', views.campaign_create, name='campaign_create'),
    path('publisher/campaign/<int:campaign_id>/edit/', views.campaign_edit, name='campaign_edit'),
    path('brand/field-reps/', views.field_rep_list, name='field_rep_list'),
    path('field/send/', views.share_collateral, name='share_collateral'),
    path('field/doctors/', views.doctor_status_list, name='doctor_status_list'),
    path('doctor/verify/<str:token>/', views.doctor_verify, name='doctor_verify'),
    path('doctor/landing/<str:token>/', views.doctor_landing, name='doctor_landing'),
    path('activity/<int:share_id>/<str:event_type>/', views.track_activity, name='track_activity'),
]
