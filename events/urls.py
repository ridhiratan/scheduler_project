from rest_framework.routers import DefaultRouter
from .views import EventViewSet, ReservationViewSet, SignupView
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register('events', EventViewSet, basename='event')
router.register('reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', obtain_auth_token, name='api_token_auth'),  # takes username+password and returns token
    path('', include(router.urls)),
    #for browsable api login/logout
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
