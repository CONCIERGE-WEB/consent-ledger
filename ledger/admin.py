from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Subquery

from .models import ConsentEvent, Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("phone", "name", "consent_status", "created_at")
    list_filter = ("created_at",)
    search_fields = ("phone", "name")
    readonly_fields = ("created_at",)
    ordering = ("phone",)

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + (("phone",) if obj else ())

    def get_queryset(self, request):
        latest_event = ConsentEvent.objects.filter(contact_id=OuterRef("pk")).order_by(
            "-recorded_at", "-pk"
        )
        return super().get_queryset(request).annotate(
            _latest_event_type=Subquery(latest_event.values("event_type")[:1])
        )

    @admin.display(description="Situação do consentimento", ordering="_latest_event_type")
    def consent_status(self, obj):
        return {
            ConsentEvent.EventType.OPTED_IN: "Com consentimento registrado",
            ConsentEvent.EventType.OPTED_OUT: "Descadastrado",
        }.get(obj._latest_event_type, "Sem registro")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConsentEvent)
class ConsentEventAdmin(admin.ModelAdmin):
    list_display = ("contact", "event_type", "source", "recorded_at", "recorded_by")
    list_filter = ("event_type", "recorded_at")
    search_fields = ("contact__phone", "contact__name", "source", "evidence")
    autocomplete_fields = ("contact",)
    readonly_fields = ("recorded_at", "recorded_by")
    ordering = ("-recorded_at", "-pk")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return tuple(field.name for field in self.model._meta.fields)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            raise ValidationError("Eventos históricos não podem ser alterados.")
        obj.recorded_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False
