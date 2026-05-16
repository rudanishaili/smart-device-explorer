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
]