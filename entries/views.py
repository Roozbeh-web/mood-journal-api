from rest_framework import generics
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