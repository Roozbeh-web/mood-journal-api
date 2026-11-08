from django.urls import path
from .views import EntryListCreateView, EntryDetailView, EntryStatsView

urlpatterns = [
    path('entries/', EntryListCreateView.as_view(), name='entry-list'),
    path('entries/stats/', EntryStatsView.as_view(), name='entry-stats'),
    path('entries/<int:pk>/', EntryDetailView.as_view(), name='entry-detail'),
]