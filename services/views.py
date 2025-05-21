from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ServiceProvider, ServiceRequest, Match
from .serializers import ServiceProviderSerializer, ServiceRequestSerializer, MatchSerializer
from geopy.distance import geodesic
import requests

@api_view(['POST'])
def register_provider(request):
    serializer = ServiceProviderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "سرویس‌دهنده ثبت شد.", "data": serializer.data})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def request_service(request):
    serializer = ServiceRequestSerializer(data=request.data)
    if serializer.is_valid():
        service_request = serializer.save()
        # جستجو برای تطبیق
        providers = ServiceProvider.objects.filter(category=service_request.category, city=service_request.city)
        for p in providers:
            distance = geodesic((p.lat, p.lng), (service_request.lat, service_request.lng)).km
            if distance <= 5:
                match = Match.objects.create(provider=p, request=service_request)
                return Response({"message": "تطبیق موفق", "provider": ServiceProviderSerializer(p).data})
        return Response({"message": "در این منطقه کسی یافت نشد"})
    return Response(serializer.errors, status=400)





def create_addon():
    token = "AadMzx0b"
    url = f"https://api.divar.ir/v2/open-platform/addons/post/{token}"
    headers = {
        "x-api-key": "your_actual_api_key_here",
        "Content-Type": "application/json"
    }
    payload = {
        "title": "ثبت موقعیت تعمیرکار",
        "description": "لطفاً موقعیت مکانی خود را برای دریافت درخواست ثبت کنید.",
        "city": "تهران",
        "district": "تجریش",
        "location": {
            "lat": 35.81417,
            "lng": 51.42528
        },
        "category": "تعمیر کولر گازی"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()