from rest_framework import serializers
from .models import Event, Reservation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id','title','description','category','start_time','end_time',
                  'capacity','creator','available_slots','created_at']

    def get_available_slots(self, obj):
        return obj.available_slots()

class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id','event','user','created_at','cancelled']
        read_only_fields = ['user','created_at']
