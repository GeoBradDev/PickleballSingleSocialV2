from django.contrib import admin
from django.urls import path

from api.views import api, stripe_webhook

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
    path("api/", api.urls),
]
