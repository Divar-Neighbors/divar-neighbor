

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import ServiceProvider, ServiceRequest, Match
from .serializers import ServiceProviderSerializer, ServiceRequestSerializer, MatchSerializer
from geopy.distance import geodesic
import requests
import json

# اطلاعات کلاینت OAuth دیوار
CLIENT_ID = '1c8556b0-34fd-11f0-8be3-12d73c7dbe6b'
CLIENT_SECRET = '163291bb061304b667f2482c4e7beee78a9a92e76ff8eaaf9767ef5daecbf876426067f1b691f2a7d39884e1887442a393b3de321b2ab888b77dbd9b58733ede'  # جایگزین کن
REDIRECT_URI = 'https://18e4-82-115-24-48.ngrok-free.app/oauth/callback'
AUTH_URL = 'https://auth.divar.ir/oauth/authorize'
TOKEN_URL = 'https://auth.divar.ir/oauth/token'
SCOPE = 'USER_ADDON_CREATE USER_PHONE_NUMBER'

@api_view(['POST'])
def register_provider(request):
    serializer = ServiceProviderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "سرویس‌دهنده ثبت شد.", "data": serializer.data})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def start_request_with_oauth(request):
    request.session['pending_request'] = request.data
    auth_redirect_url = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
    )
    return redirect(auth_redirect_url)

@api_view(['GET'])
def oauth_callback(request):
    code = request.GET.get('code')
    if not code:
        return Response({"error": "کد تایید موجود نیست"}, status=400)

    # درخواست برای گرفتن access token
    token_response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    if token_response.status_code != 200:
        return Response({"error": "دریافت access token شکست خورد", "details": token_response.text}, status=400)

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    data = request.session.get('pending_request')
    if not data:
        return Response({"error": "اطلاعات درخواست وجود ندارد."}, status=400)

    serializer = ServiceRequestSerializer(data=data)
    if serializer.is_valid():
        service_request = serializer.save()
        providers = ServiceProvider.objects.filter(category=service_request.category, city=service_request.city)
        for p in providers:
            distance = geodesic((p.lat, p.lng), (service_request.lat, service_request.lng)).km
            if distance <= 5:
                Match.objects.create(provider=p, request=service_request)

                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                addon_payload = {
                    "title": "درخواست خدمات",
                    "description": f"{service_request.name} نیاز به {service_request.category} دارد.",
                    "location": {
                        "lat": service_request.lat,
                        "lng": service_request.lng
                    },
                    "category": service_request.category
                }
                post_token = data.get("post_token")
                addon_url = f"https://divar.ir/kenar/api/v2/open-platform/addons/post/{post_token}"
                addon_res = requests.post(addon_url, headers=headers, json=addon_payload)

                return Response({
                    "message": "تطبیق موفق + افزونه ثبت شد",
                    "provider": ServiceProviderSerializer(p).data,
                    "divar_response": addon_res.json(),
                    "access_token": token_data
                })
        return Response({"message": "در این منطقه کسی یافت نشد", "access_token": token_data})
    return Response(serializer.errors, status=400)


# from django.conf import Settings
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.shortcuts import redirect
# from django.http import HttpResponse
# from .models import ServiceProvider, ServiceRequest, Match
# from .serializers import ServiceProviderSerializer, ServiceRequestSerializer, MatchSerializer
# from geopy.distance import geodesic
# import kenar
# from django.conf import settings
# import requests
#
# # پیکربندی client دیوار
# kenar_app = kenar.Client(settings.KENAR_CLIENT_CONFIG)
#
# @api_view(['POST'])
# def register_provider(request):
#     serializer = ServiceProviderSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "سرویس‌دهنده ثبت شد.", "data": serializer.data})
#     return Response(serializer.errors, status=400)
#
# @api_view(['POST'])
# def start_request_with_oauth(request):
#     request.session['pending_request'] = request.data
#     return redirect(kenar_app.get_authorization_url(state="secure123"))
#
# @api_view(['GET'])
# def oauth_callback(request):
#     code = request.GET.get('code')
#     token_data = kenar_app.fetch_access_token(code=code)  # ← اینجا اصلاح شد
#     access_token = token_data.get("access_token")
#
#     data = request.session.get('pending_request')
#     if not data:
#         return Response({"error": "اطلاعات درخواست وجود ندارد."}, status=400)
#
#     serializer = ServiceRequestSerializer(data=data)
#     if serializer.is_valid():
#         service_request = serializer.save()
#         providers = ServiceProvider.objects.filter(category=service_request.category, city=service_request.city)
#         for p in providers:
#             distance = geodesic((p.lat, p.lng), (service_request.lat, service_request.lng)).km
#             if distance <= 5:
#                 Match.objects.create(provider=p, request=service_request)
#
#                 headers = {
#                     "Authorization": f"Bearer {access_token}",
#                     "Content-Type": "application/json"
#                 }
#                 addon_payload = {
#                     "title": "درخواست خدمات",
#                     "description": f"{service_request.name} نیاز به {service_request.category} دارد.",
#                     "location": {
#                         "lat": service_request.lat,
#                         "lng": service_request.lng
#                     },
#                     "category": service_request.category
#                 }
#                 post_token = data.get("post_token")
#                 addon_url = f"https://divar.ir/kenar/api/v2/open-platform/addons/post/{post_token}"
#                 addon_res = requests.post(addon_url, headers=headers, json=addon_payload)
#
#                 return Response({
#                     "message": "تطبیق موفق + افزونه واقعی ثبت شد",
#                     "provider": ServiceProviderSerializer(p).data,
#                     "divar_response": addon_res.json(),
#                     "access_token": token_data
#                 })
#         return Response({"message": "در این منطقه کسی یافت نشد", "access_token": token_data})
#     return Response(serializer.errors, status=400)
