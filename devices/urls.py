from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mobile-explorer/', views.mobile_explorer, name='mobile_explorer'),
]