# Airdrop/signals.py

import sys
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Participant

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Prevent signal from running during migrations or createsuperuser
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv or 'createsuperuser' in sys.argv:
        return

    if created:
        Participant.objects.create(user=instance)
