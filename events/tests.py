from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Event, Registration

User = get_user_model()

class EventAPITests(APITestCase):
    def setUp(self):
        # Create test user and auth token
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Create an upcoming event
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_time=datetime.now() + timedelta(days=1),
            capacity=2
        )
        self.list_url = reverse('event-list')
        self.detail_url = reverse('event-detail', args=[self.event.pk])
        self.register_url = reverse('event-register', args=[self.event.pk])

    def test_list_events(self):
        """Any user can list events (no auth required)"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Event')
        self.assertEqual(response.data[0]['spots_taken'], 0)

    def test_get_event_detail(self):
        """Any user can view event details (no auth required)"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Event')

    def test_register_for_event_requires_auth(self):
        """Registration requires authentication"""
        response = self.client.post(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_for_event(self):
        """Authenticated user can register for an event"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(Registration.objects.first().user, self.user)

    def test_prevent_double_registration(self):
        """User cannot register for the same event twice"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        # First registration
        response1 = self.client.post(self.register_url)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        # Try to register again
        response2 = self.client.post(self.register_url)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enforce_event_capacity(self):
        """Registration should fail when event is at capacity"""
        # Create another user and register them
        user2 = User.objects.create_user(username='user2', password='pass123')
        token2 = Token.objects.create(user=user2)

        # Register first user (self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response1 = self.client.post(self.register_url)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Register second user
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token2.key}')
        response2 = self.client.post(self.register_url)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Try to register a third user
        user3 = User.objects.create_user(username='user3', password='pass123')
        token3 = Token.objects.create(user=user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token3.key}')
        response3 = self.client.post(self.register_url)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

class RegistrationAPITests(APITestCase):
    def setUp(self):
        # Create test user and auth token
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Create an event and register the user
        self.event = Event.objects.create(
            title='Test Event',
            start_time=datetime.now() + timedelta(days=1)
        )
        self.registration = Registration.objects.create(
            user=self.user,
            event=self.event
        )
        self.list_url = reverse('my-registrations')
        self.cancel_url = reverse('cancel-registration', args=[self.registration.pk])

    def test_list_my_registrations(self):
        """User can list their registrations"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event']['title'], 'Test Event')

    def test_list_registrations_requires_auth(self):
        """Listing registrations requires authentication"""
        self.client.credentials()  # Clear auth
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancel_registration(self):
        """User can cancel their registration"""
        response = self.client.post(self.cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.registration.refresh_from_db()
        self.assertTrue(self.registration.cancelled)

    def test_prevent_double_cancellation(self):
        """Cannot cancel an already cancelled registration"""
        # Cancel first time
        response1 = self.client.post(self.cancel_url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Try to cancel again
        response2 = self.client.post(self.cancel_url)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_others_registration(self):
        """User cannot cancel another user's registration"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123'
        )
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        response = self.client.post(self.cancel_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.registration.refresh_from_db()
        self.assertFalse(self.registration.cancelled)