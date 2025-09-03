from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='plate_form'), name='home'),
    path('form/', views.PlateFormView.as_view(), name='plate_form'),
    path('success/', views.success_view, name='plate_success'),
    path('download/<str:cod_envio>/', views.download_pdf_view, name='download_pdf'),
]