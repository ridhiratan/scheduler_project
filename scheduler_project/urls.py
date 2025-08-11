from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Event Scheduler API. Visit /api/events/ for the event list.")

urlpatterns = [
    path('', home),  # now root URL works
    path('admin/', admin.site.urls),
    path('api/', include('events.urls')),
]
