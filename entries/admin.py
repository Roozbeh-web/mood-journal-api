from django.contrib import admin
from .models import Entry

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'mood_score')
    list_filter = ('user',)
    search_fields = ('text',)
    
