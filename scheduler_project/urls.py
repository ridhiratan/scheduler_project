from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'events/home.html')

urlpatterns = [
    path('', home),  # now root URL works
    path('admin/', admin.site.urls),
    path('api/', include('events.urls')),
]
