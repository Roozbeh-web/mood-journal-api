from rest_framework import serializers
from .models import Entry
from .mood import analyze_mood

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['id', 'text', 'mood_score', 'created_at']
        read_only_fields = ['id', 'mood_score', 'created_at']

    def create(self, validated_data):
        text = validated_data['text']
        validated_data['mood_score'] = analyze_mood(text)
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'text' in validated_data:
            validated_data['mood_score'] = analyze_mood(validated_data['text'])
        return super().update(instance, validated_data)