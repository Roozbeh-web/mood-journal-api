from django.db.models import Avg, Count, Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Entry
from .serializers import EntrySerializer

class EntryListCreateView(generics.ListCreateAPIView):
    serializer_class = EntrySerializer
    
    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)
    
class EntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EntrySerializer

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

class EntryStatsView(APIView):
    def get(self, request):
        qs = Entry.objects.filter(user=request.user)
        stats = qs.aggregate(
            total_entries=Count('id'),
            average_mood=Avg('mood_score'),
            positive_entries=Count('id', filter=Q(mood_score__gt=0.1)),
            negative_entries=Count('id', filter=Q(mood_score__lt=-0.1)),
            neutral_entries=Count('id', filter=Q(mood_score__gte=-0.1, mood_score__lte=0.1)),
        )
        return Response(stats)