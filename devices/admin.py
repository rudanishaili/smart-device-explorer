from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from .models import Device, Favorite, Review
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'brand',
        'price',
        'ram',
        'storage',
        'usage_tag',
        'ai_score',
        'average_rating',
        'favorite_count',
    )

    list_filter = (
        'category',
        'brand',
        'usage_tag',
    )

    search_fields = (
        'name',
        'brand',
        'processor',
    )

    def average_rating(self, obj):
        avg = obj.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']

        if avg:
            return round(avg, 1)

        return 0

    average_rating.short_description = 'Avg Rating'

    def favorite_count(self, obj):
        return Favorite.objects.filter(device=obj).count()

    favorite_count.short_description = 'Favorites'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'device',
        'device_category',
        'added_at',
    )

    list_filter = (
        'device__category',
        'device__brand',
    )

    search_fields = (
        'user__username',
        'device__name',
        'device__brand',
    )

    def device_category(self, obj):
        return obj.device.category

    device_category.short_description = 'Category'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'device',
        'rating',
        'reaction',
        'created_at',
    )

    list_filter = (
        'rating',
        'reaction',
        'device__category',
        'device__brand',
    )

    search_fields = (
        'user__username',
        'device__name',
        'comment',
    )


original_index = admin.site.index


def custom_admin_index(request, extra_context=None):

    total_devices = Device.objects.count()
    total_users = User.objects.count()
    total_favorites = Favorite.objects.count()
    total_reviews = Review.objects.count()

    top_brands = (
        Device.objects
        .values('brand')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    context = {
        **admin.site.each_context(request),
        'title': 'Aether Admin Dashboard',
        'total_devices': total_devices,
        'total_users': total_users,
        'total_favorites': total_favorites,
        'total_reviews': total_reviews,
        'top_brands': top_brands,
    }

    return TemplateResponse(
        request,
        'admin/index.html',
        context
    )


admin.site.index = custom_admin_index