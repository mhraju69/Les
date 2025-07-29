# airdrop/views.py

import csv
import random
import string
import requests
from .models import Participant
from django.conf import settings
from urllib.parse import urljoin
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from .serializers import ParticipantSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken



def generate_referral_code(length=10):
    characters = string.ascii_uppercase + string.digits  # A-Z + 0-9
    referral_code = "".join(random.choice(characters) for _ in range(length))
    return referral_code

class RegisterView(APIView):
        # permission_classes = [IsAuthenticated]
        def post(self, request):
            referred_by = request.GET.get('reff', None)
            wallet = request.data.get('wallet')
            twitter = request.data.get('twitter')
            retweet = request.data.get('retweet')
            telegram = request.data.get('telegram')            
            referral_code = generate_referral_code()
            email = request.data.get('email')

            Participant.objects.filter(email=email).update(
                referred_by=referred_by,
                twitter=twitter,
                retweet=retweet,
                referral_code=referral_code,
                telegram=telegram,
                points=5000,
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
    def get(self, request, *args, **kwargs):
        wallet = kwargs.get('wallet') 
        print(f"Received wallet: {wallet}")
        if not wallet:
            return Response({"error": "Wallet parameter is required"}, status=400)
        participants = Participant.objects.filter(wallet=wallet)

        if not participants.exists():
            return Response({"error": "No participant found for this wallet"}, status=404)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="participants.csv"'

        writer = csv.writer(response)
        writer.writerow(['Wallet','Email', 'Points', 'Referral Code', 'Referred By'])
        for p in participants:
            writer.writerow([p.wallet, p.email, p.points, p.referral_code, p.referred_by])

        return response

def login(request):
        return render(request, "pages/login.html",{
            'google_client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'google_callback_uri': settings.GOOGLE_OAUTH_CALLBACK_URL,
        })


class SocialAuthCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        print(f"Received code: {code} from Google OAuth callback")
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
        
        participant, created = Participant.objects.get_or_create(email=email)

        refresh = RefreshToken.for_user(participant)
        context = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": email,
                "name": name,
            }
        }

        if not created:
            participant = Participant.objects.get(email=email)
            serializer = ParticipantSerializer(participant)
            return Response({'data': serializer.data, 'usertype': "old",'context': context}, status=status.HTTP_200_OK)


        return Response({'usertype': "new", 'context': context}, status=status.HTTP_201_CREATED)
