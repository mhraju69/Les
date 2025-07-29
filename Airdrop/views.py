# airdrop/views.py

import csv
import random
import string
import requests
from .models import Participant
from django.conf import settings
from urllib.parse import urljoin
from rest_framework import status
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from .serializers import ParticipantSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
User = get_user_model()

def generate_referral_code(length=10):
    characters = string.ascii_uppercase + string.digits  # A-Z + 0-9
    referral_code = "".join(random.choice(characters) for _ in range(length))
    return referral_code

class RegisterView(APIView):
        permission_classes = [IsAuthenticated]

        def get(self, request):
            participant = Participant.objects.filter(user=request.user).first()
            if participant:
                return Response(ParticipantSerializer(participant).data, status=status.HTTP_200_OK)
            return Response({'error': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        def patch(self, request):
            participant = Participant.objects.filter(user=request.user).first()
            referred_by = request.GET.get('reff', None)
            wallet = request.data.get('wallet')
            twitter = request.data.get('twitter')
            retweet = request.data.get('retweet')
            telegram = request.data.get('telegram')            
            referral_code = generate_referral_code() if  participant.referral_code is None else participant.referral_code
            
            
            point = participant.points
            
            if wallet and not participant.wallet :
                point+=1000
            if twitter and not participant.twitter:
                point+=1000
            if retweet and not participant.retweet:
                point+=1000
            if telegram and not participant.telegram:
                point+=2000



            Participant.objects.filter(user=request.user).update(
                referred_by=referred_by,
                twitter=twitter,
                retweet=retweet,
                referral_code=referral_code,
                telegram=telegram,
                points=point,
                wallet=wallet)


            if referred_by:
                try:
                    referrer = Participant.objects.get(referral_code=referred_by)
                    referrer.points += 200  # Add referral bonus
                    referrer.save()
                except:
                    pass
            return Response({'referral_link':referral_code}, status=status.HTTP_201_CREATED)
            

# airdrop/views.py (continued)


class ExportCSVView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        participants = Participant.objects.filter(user=request.user)
        if not participants:
            return Response({'error': 'No participants found'}, status=status.HTTP_404_NOT_FOUND)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Participants.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name','Email','Wallet', 'Points', 'Referral Code', 'Referred By'])
        for p in participants:
            writer.writerow([p.user.first_name, p.user.email,p.wallet, p.points, p.referral_code, p.referred_by])

        return response

def login(request):
        return render(request, "pages/login.html",{
            'google_client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'google_callback_uri': settings.GOOGLE_OAUTH_CALLBACK_URL,
        })


class SocialAuthCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        # Step 1: Exchange code for access_token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
            "grant_type": "authorization_code",
        }

        token_res = requests.post(token_url, data=data)
        if token_res.status_code != 200:
            return Response({"error": "Failed to get token"}, status=400)

        token_json = token_res.json()
        access_token = token_json.get("access_token")

        # Step 2: Get user info from Google
        userinfo_res = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_res.status_code != 200:
            return Response({"error": "Failed to fetch user info"}, status=400)

        user_info = userinfo_res.json()
        email = user_info.get("email")
        name = user_info.get("name")

        # সমাধান: সঠিকভাবে get_or_create ব্যবহার
        user, created = User.objects.get_or_create(
            email=email,  # ইউনিক ফিল্ড হিসেবে email ব্যবহার
            defaults={
                'username': email,
                'first_name': name,
                'password': make_password(None)
            }
        )
        if created:
            Participant.objects.create(user=user)
        
        refresh = RefreshToken.for_user(user)
        context = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": email,
                "name": name,
            }
        }

        return Response({
            'usertype': "new" if created else 'old', 
            'context': context
        }, status=status.HTTP_201_CREATED)