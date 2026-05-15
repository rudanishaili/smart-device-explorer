from django.contrib import admin
from .models import Device,Favorite


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'ram', 'storage', 'usage_tag', 'ai_score')
    list_filter = ('brand', 'usage_tag')
    search_fields = ('name', 'brand', 'processor')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'added_at')