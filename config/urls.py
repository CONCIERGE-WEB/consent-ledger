from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def healthz(_request):
    return JsonResponse({"status": "ok"})


admin.site.site_header = "Consent Ledger"
admin.site.site_title = "Consent Ledger"
admin.site.index_title = "Registro de consentimentos"

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("admin/", admin.site.urls),
]
