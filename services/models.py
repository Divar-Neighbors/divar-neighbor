from django.db import models

class ServiceProvider(models.Model):
    objects = None
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    category = models.CharField(max_length=100)  # مثلاً "تعمیر کولر گازی"
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    lat = models.FloatField()
    lng = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class ServiceRequest(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    category = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    lat = models.FloatField()
    lng = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    matched = models.BooleanField(default=False)

class Match(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)