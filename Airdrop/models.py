# airdrop/models.py

from django.db import models

class Participant(models.Model):
    email = models.EmailField(max_length=255, unique=True)
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
        return self.email