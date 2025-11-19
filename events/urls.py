from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:pk>/register/', views.RegisterView.as_view(), name='event-register'),

    path('registrations/', views.MyRegistrationsView.as_view(), name='my-registrations'),
    path('registrations/<int:pk>/cancel/', views.CancelRegistrationView.as_view(), name='cancel-registration'),
]
