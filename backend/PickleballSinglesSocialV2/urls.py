from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from api.views import api, stripe_webhook


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check),
    path("admin/", admin.site.urls),
    path("api/webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
    path("api/", api.urls),
]
