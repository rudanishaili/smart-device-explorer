from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mobile-explorer/', views.mobile_explorer, name='mobile_explorer'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('favorites/', views.favorites, name='favorites'),

    path(
        'add-to-favorites/<int:device_id>/',
        views.add_to_favorites,
        name='add_to_favorites'
    ),

    path(
        'remove-from-favorites/<int:device_id>/',
        views.remove_from_favorites,
        name='remove_from_favorites'
    ),

    path('compare/', views.compare_devices, name='compare'),

    path('device/<int:device_id>/', views.device_detail, name='device_detail'),

    path('laptop-explorer/', views.laptop_explorer, name='laptop_explorer'),

    path(
        'laptop-recommendations/',
        views.laptop_recommendations,
        name='laptop_recommendations'
    ),

    path('laptop-favorites/', views.laptop_favorites, name='laptop_favorites'),
    path('laptop-compare/', views.laptop_compare, name='laptop_compare'),
    path('device/<int:device_id>/review/', views.add_review, name='add_review'),
    path(
    'ai-device-analyzer/',
    views.ai_device_analyzer,
    name='ai_device_analyzer'
),
]