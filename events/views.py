from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all().order_by('start_time')
    serializer_class = EventSerializer


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class RegisterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        # check for existing registration
        if Registration.objects.filter(user=request.user, event=event, cancelled=False).exists():
            return Response({'detail': 'Already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        # check capacity
        if event.capacity is not None:
            taken = event.registrations.filter(cancelled=False).count()
            if taken >= event.capacity:
                return Response({'detail': 'Event is full.'}, status=status.HTTP_400_BAD_REQUEST)
        reg = Registration.objects.create(user=request.user, event=event)
        serializer = RegistrationSerializer(reg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)


class CancelRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk, user=request.user)
        if reg.cancelled:
            return Response({'detail': 'Already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        reg.cancelled = True
        reg.save()
        return Response({'detail': 'Cancelled.'}, status=status.HTTP_200_OK)
