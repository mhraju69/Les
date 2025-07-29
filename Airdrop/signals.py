# Airdrop/signals.py
import sys
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Participant

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Skip during migrations, tests, or shell commands
    if any(command in sys.argv for command in [
        'makemigrations',
        'migrate',
        'createsuperuser',
        'shell',
        'test'
    ]):
        return

    if created:
        try:
            Participant.objects.create(user=instance)
        except Exception as e:
            print(f"Could not create Participant: {e}")
