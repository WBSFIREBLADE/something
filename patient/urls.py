from django.urls import path

from . import views

urlpatterns = [
    path('patient/', views.patient_list_create, name='patient_list_create'),
    path('patient/new/', views.patient_create, name='patient_create'),
    path('patient/<int:pk>/', views.patient_detail, name='patient_detail'),
]
