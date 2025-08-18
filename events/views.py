from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Event, Reservation
from .serializers import EventSerializer, ReservationSerializer, UserSerializer
from .permissions import IsCreatorOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

class SignupView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Simple signup handling: username + password
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        if not username or not password:
            return Response({'detail': 'username and password required'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'username already exists'}, status=400)
        user = User.objects.create_user(username=username, password=password, email=email)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=201)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-start_time')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['get','post'], permission_classes=[permissions.IsAuthenticated])
    def reserve(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        if request.method == 'POST':
            # Wrap in a transaction to make this operation atomic
            with transaction.atomic():
                # Lock the event row
                locked_event = Event.objects.select_for_update().get(pk=event.pk)

                # prevent duplicate reservation
                already = Reservation.objects.filter(event=locked_event, user=request.user, cancelled=False).exists()
                if already:
                    return Response({'detail': 'You already reserved this event'}, status=status.HTTP_400_BAD_REQUEST)

                # check capacity
                current = locked_event.reservations.filter(cancelled=False).count()
                if current >= locked_event.capacity:
                    return Response({'detail': 'Event is full'}, status=status.HTTP_400_BAD_REQUEST)

                # all good -> create reservation
                reservation = Reservation.objects.create(event=locked_event, user=request.user)
                return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)
        else:
            # GET request → show a dummy form in browsable API
            return Response({"detail": "Click POST to reserve this event"})


    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def reservations(self, request, pk=None):
        """
        Creator can see who reserved for their event.
        """
        event = get_object_or_404(Event, pk=pk)
        if event.creator != request.user:
            return Response({'detail': 'Forbidden'}, status=403)
        qs = event.reservations.filter(cancelled=False)
        return Response(ReservationSerializer(qs, many=True).data)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all().order_by('-created_at')
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # users can see only their reservations unless they are the event creator and call event reservations
        return Reservation.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Allow users to cancel their reservation (soft cancel)
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'detail':'Not allowed'}, status=403)
        instance.cancelled = True
        instance.save()
        return Response(status=204)
