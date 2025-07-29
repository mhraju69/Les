from django.contrib import admin
from django.urls import path,include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('airdrop/', include('Airdrop.urls'), name='airdrop'),
]
