from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def mobile_explorer(request):
    return render(request, 'mobile_explorer.html')