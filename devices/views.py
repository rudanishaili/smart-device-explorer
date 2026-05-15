from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Device, Favorite


def home(request):
    return render(request, 'home.html')


def mobile_explorer(request):
    return render(request, 'mobile_explorer.html')


def recommendations(request):

    recommended_devices = []
    favorite_device_ids = []

    if request.user.is_authenticated:
        favorite_device_ids = list(
            Favorite.objects.filter(user=request.user)
            .values_list('device_id', flat=True)
        )

    # SAVE FILTERS
    if request.method == "POST":

        request.session['brand'] = request.POST.get("brand")
        request.session['budget'] = request.POST.get("budget")
        request.session['usage'] = request.POST.get("usage")

    # GET FILTERS
    brand = request.session.get('brand')
    budget = request.session.get('budget')
    usage = request.session.get('usage')

    if brand and budget and usage:

        budget = int(budget)

        devices = Device.objects.filter(
            brand__icontains=brand,
            price__lte=budget
        )

        for device in devices:

            score = 0

            if device.price <= budget:
                score += 30

            if device.ram:
                ram_value = int(device.ram.replace("GB", ""))

                if ram_value >= 8:
                    score += 30
                elif ram_value >= 4:
                    score += 20

            if device.storage:
                storage_value = int(device.storage.replace("GB", ""))

                if storage_value >= 256:
                    score += 25
                elif storage_value >= 128:
                    score += 15

            if usage == "gaming" and device.ram in ["8GB", "12GB", "16GB"]:
                score += 15
            elif usage == "camera":
                score += 10
            elif usage == "daily":
                score += 10

            recommended_devices.append({
                'device': device,
                'score': score
            })

        recommended_devices.sort(
            key=lambda x: x['score'],
            reverse=True
        )

    return render(
        request,
        'recommendations.html',
        {
            'recommended_devices': recommended_devices,
            'favorite_device_ids': favorite_device_ids
        }
    )

def add_to_favorites(request, device_id):

    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Login required'
        })

    device = Device.objects.get(id=device_id)

    Favorite.objects.get_or_create(
        user=request.user,
        device=device
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Added to favorites',
        'device_id': device.id
    })


def favorites(request):

    favorite_items = Favorite.objects.filter(
        user=request.user
    )

    return render(
        request,
        'favorites.html',
        {'favorite_items': favorite_items}
    )

def remove_from_favorites(request, device_id):

    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Login required'
        })

    Favorite.objects.filter(
        user=request.user,
        device_id=device_id
    ).delete()

    return JsonResponse({
        'status': 'success',
        'message': 'Removed from favorites',
        'device_id': device_id
    })