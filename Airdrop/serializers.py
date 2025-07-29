# airdrop/serializers.py

from rest_framework import serializers
from .models import Participant

class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = '__all__'

    def get_user(self, obj):
        return obj.user.email if obj.user else None