from rest_framework import serializers
from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
    spots_taken = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'start_time', 'end_time', 'capacity', 'spots_taken']

    def get_spots_taken(self, obj):
        return obj.registrations.filter(cancelled=False).count()


class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), source='event', write_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'event', 'event_id', 'created_at', 'cancelled']
        read_only_fields = ['id', 'created_at', 'event']
