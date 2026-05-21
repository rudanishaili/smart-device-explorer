from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Device, Favorite, Review
from django.contrib.auth.decorators import login_required
import google.generativeai as genai
from django.conf import settings


def home(request):
    return render(request, 'home.html')


def mobile_explorer(request):
    return render(request, 'mobile_explorer.html')


def laptop_explorer(request):
    return render(request, 'laptop_explorer.html')


def recommendations(request):

    recommended_devices = []
    favorite_device_ids = []

    if request.user.is_authenticated:
        favorite_device_ids = list(
            Favorite.objects.filter(
                user=request.user,
                device__category='mobile'
            ).values_list('device_id', flat=True)
        )

    if request.method == "POST":
        request.session['brand'] = request.POST.get("brand")
        request.session['budget'] = request.POST.get("budget")
        request.session['usage'] = request.POST.get("usage")

    brand = request.session.get('brand')
    budget = request.session.get('budget')
    usage = request.session.get('usage')

    search = request.GET.get("search", "")
    max_price = request.GET.get("max_price", "")
    ram_filter = request.GET.get("ram", "")
    storage_filter = request.GET.get("storage", "")

    if brand and budget and usage:

        budget = int(budget)

        devices = Device.objects.filter(
            category='mobile',
            brand__icontains=brand,
            price__lte=budget
        )

        if search:
            devices = devices.filter(name__icontains=search)

        if max_price:
            devices = devices.filter(price__lte=max_price)

        if ram_filter:
            devices = devices.filter(ram__icontains=ram_filter)

        if storage_filter:
            devices = devices.filter(storage__icontains=storage_filter)

        for device in devices:

            score = 0

            if device.price <= budget:
                score += 30

            if device.ram:
                try:
                    ram_value = int(device.ram.replace("GB", "").strip())

                    if ram_value >= 8:
                        score += 30
                    elif ram_value >= 4:
                        score += 20
                except:
                    pass

            if device.storage:
                try:
                    storage_value = int(device.storage.replace("GB", "").strip())

                    if storage_value >= 256:
                        score += 25
                    elif storage_value >= 128:
                        score += 15
                except:
                    pass

            if usage == "gaming" and device.ram in ["8GB", "12GB", "16GB"]:
                score += 15
            elif usage == "camera":
                score += 10
            elif usage == "daily":
                score += 10

            recommended_devices.append({
                'device': device,
                'score': min(score, 100)
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
            'favorite_device_ids': favorite_device_ids,
            'search': search,
            'max_price': max_price,
            'ram_filter': ram_filter,
            'storage_filter': storage_filter,
        }
    )

def laptop_recommendations(request):

    recommended_devices = []
    favorite_device_ids = []

    if request.user.is_authenticated:
        favorite_device_ids = list(
            Favorite.objects.filter(
                user=request.user,
                device__category='laptop'
            ).values_list('device_id', flat=True)
        )

    if request.method == "POST":
        request.session['laptop_brand'] = request.POST.get("brand")
        request.session['laptop_budget'] = request.POST.get("budget")
        request.session['laptop_usage'] = request.POST.get("usage")

    brand = request.session.get('laptop_brand')
    budget = request.session.get('laptop_budget')
    usage = request.session.get('laptop_usage')

    search = request.GET.get("search", "")
    max_price = request.GET.get("max_price", "")
    ram_filter = request.GET.get("ram", "")
    storage_filter = request.GET.get("storage", "")
    processor_filter = request.GET.get("processor", "")

    if brand and budget and usage:

        budget = int(budget)

        devices = Device.objects.filter(
            category='laptop',
            brand__icontains=brand,
            price__lte=budget
        )

        if search:
            devices = devices.filter(name__icontains=search)

        if max_price:
            devices = devices.filter(price__lte=max_price)

        if ram_filter:
            devices = devices.filter(ram__icontains=ram_filter)

        if storage_filter:
            devices = devices.filter(storage__icontains=storage_filter)

        if processor_filter:
            devices = devices.filter(processor__icontains=processor_filter)

        for device in devices:

            score = 50

            if device.ram:
                try:
                    ram = int(device.ram.replace("GB", "").strip())

                    if ram >= 16:
                        score += 25
                    elif ram >= 8:
                        score += 15
                except:
                    pass

            if device.storage:
                try:
                    storage = int(device.storage.replace("GB", "").strip())

                    if storage >= 512:
                        score += 20
                    elif storage >= 256:
                        score += 10
                except:
                    pass

            if usage == "gaming":
                score += 10
            elif usage == "coding":
                score += 10
            elif usage == "editing":
                score += 15
            elif usage == "student":
                score += 5

            recommended_devices.append({
                'device': device,
                'score': min(score, 100)
            })

        recommended_devices.sort(
            key=lambda x: x['score'],
            reverse=True
        )

    return render(
        request,
        'laptop_recommendations.html',
        {
            'recommended_devices': recommended_devices,
            'favorite_device_ids': favorite_device_ids,
            'search': search,
            'max_price': max_price,
            'ram_filter': ram_filter,
            'storage_filter': storage_filter,
            'processor_filter': processor_filter,
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
        user=request.user,
        device__category='mobile'
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


def compare_devices(request):

    device_ids = request.GET.getlist('devices')

    devices = Device.objects.filter(id__in=device_ids)

    return render(
        request,
        'compare.html',
        {'devices': devices}
    )


def compare_devices(request):

    device_ids = request.GET.getlist('devices')

    devices = Device.objects.filter(id__in=device_ids)

    best_device = None
    best_score = -1

    for device in devices:

        score = 0

        if device.ram:
            ram_value = int(device.ram.replace("GB", ""))
            score += ram_value * 3

        if device.storage:
            storage_value = int(device.storage.replace("GB", ""))
            score += storage_value * 0.2

        if device.price:
            score += max(0, 30 - (device.price / 3000))

        if score > best_score:
            best_score = score
            best_device = device

    return render(
        request,
        'compare.html',
        {
            'devices': devices,
            'best_device': best_device,
            'best_score': round(best_score, 2)
        }
    )


def device_detail(request, device_id):

    device = Device.objects.get(id=device_id)

    is_favorite = False

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            device=device
        ).exists()

    reviews = Review.objects.filter(
        device=device
    ).order_by('-created_at')

    average_rating = 0

    if reviews.exists():

        total = 0

        for review in reviews:
            total += review.rating

        average_rating = round(total / reviews.count(), 1)

    likes_count = reviews.filter(reaction='like').count()
    dislikes_count = reviews.filter(reaction='dislike').count()

    return render(
        request,
        'device_detail.html',
        {
            'device': device,
            'is_favorite': is_favorite,
            'reviews': reviews,
            'average_rating': average_rating,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
        }
    )


def laptop_favorites(request):

    favorite_items = Favorite.objects.filter(
        user=request.user,
        device__category='laptop'
    )

    return render(
        request,
        'laptop_favorites.html',
        {'favorite_items': favorite_items}
    )

def laptop_compare(request):

    device_ids = request.GET.getlist('devices')

    devices = Device.objects.filter(
        id__in=device_ids,
        category='laptop'
    )

    best_device = None
    best_score = -1

    for device in devices:

        score = 0

        if device.ram:
            try:
                ram_value = int(device.ram.replace("GB", "").strip())
                score += ram_value * 3
            except:
                pass

        if device.storage:
            try:
                storage_value = int(device.storage.replace("GB", "").strip())
                score += storage_value * 0.15
            except:
                pass

        if device.price:
            score += max(0, 40 - (device.price / 4000))

        if score > best_score:
            best_score = score
            best_device = device

    return render(
        request,
        'laptop_compare.html',
        {
            'devices': devices,
            'best_device': best_device,
            'best_score': round(best_score, 2)
        }
    )


@login_required
def add_review(request, device_id):

    if request.method == "POST":

        device = Device.objects.get(id=device_id)

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        reaction = request.POST.get("reaction")

        Review.objects.update_or_create(
            user=request.user,
            device=device,
            defaults={
                "rating": rating,
                "comment": comment,
                "reaction": reaction,
            }
        )

    return redirect(f"/device/{device_id}/")

def ai_device_analyzer(request):

    result = None
    uploaded_image = None

    if request.method == "POST":

        image = request.FILES.get("device_image")

        if image:

            uploaded_image = image

            genai.configure(api_key=settings.GEMINI_API_KEY)

            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = """
            Analyze this image and identify the device.
            Tell:
            1. Is it mobile or laptop?
            2. Possible brand/model
            3. Main visible features
            4. Estimated usage type
            5. Short buying suggestion
            Keep answer clear and student-project friendly.
            """

            response = model.generate_content([
                prompt,
                {
                    "mime_type": image.content_type,
                    "data": image.read()
                }
            ])

            result = response.text

    return render(
        request,
        "ai_device_analyzer.html",
        {
            "result": result,
            "uploaded_image": uploaded_image
        }
    )