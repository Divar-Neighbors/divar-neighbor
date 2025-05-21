from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ServiceProvider, ServiceRequest, Match
from .serializers import ServiceProviderSerializer, ServiceRequestSerializer, MatchSerializer
from geopy.distance import geodesic

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
        providers = ServiceProvider.objects.filter(category=service_request.category, city=service_request.city)
        for p in providers:
            distance = geodesic((p.lat, p.lng), (service_request.lat, service_request.lng)).km
            if distance <= 5:
                match = Match.objects.create(provider=p, request=service_request)
                return Response({"message": "تطبیق موفق", "provider": ServiceProviderSerializer(p).data})
        return Response({"message": "در این منطقه کسی یافت نشد"})
    return Response(serializer.errors, status=400)

# شبیه‌سازی ثبت افزونه در آگهی دیوار بدون اتصال واقعی
@api_view(['POST'])
def simulate_addon_to_post(request):
    post_token = request.data.get("post_token")
    data = {
        "title": "ثبت موقعیت تعمیرکار",
        "description": "شبیه‌سازی افزونه دیوار برای آگهی",
        "city": request.data.get("city", "تهران"),
        "district": request.data.get("district", "تجریش"),
        "location": {
            "lat": request.data.get("lat", 35.81417),
            "lng": request.data.get("lng", 51.42528)
        },
        "category": request.data.get("category", "تعمیر کولر گازی")
    }
    return Response({"message": "افزونه با موفقیت (شبیه‌سازی) ثبت شد", "post_token": post_token, "addon_data": data})


def register_provider():
    return None