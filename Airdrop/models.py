# airdrop/models.py

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participants', blank=True, null=True)
    wallet = models.CharField(max_length=255, unique=True, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    retweet = models.CharField(max_length=255, blank=True, null=True)
    telegram = models.CharField(max_length=255, blank=True, null=True)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.CharField(max_length=10, blank=True, null=True)
    points = models.PositiveIntegerField(default=0, blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    

    def refarral_count(self):
        return Participant.objects.filter(referred_by=self.referral_code).count()
    def __str__(self):
        return self.user.email
    @property
    def user_email(self):
        return self.user.email if self.user else None