from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r"^\+[1-9][0-9]{7,14}$",
    message="Use o formato internacional E.164, por exemplo +5511999999999.",
)


class Contact(models.Model):
    phone = models.CharField(max_length=16, unique=True, validators=[phone_validator])
    name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["phone"]

    def __str__(self):
        return f"{self.name} ({self.phone})" if self.name else self.phone


class ConsentEvent(models.Model):
    class EventType(models.TextChoices):
        OPTED_IN = "opted_in", "Consentimento registrado"
        OPTED_OUT = "opted_out", "Descadastro registrado"

    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="consent_events",
    )
    event_type = models.CharField(max_length=16, choices=EventType.choices)
    source = models.CharField(max_length=120)
    evidence = models.TextField()
    recorded_at = models.DateTimeField(default=timezone.now, editable=False)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        ordering = ["-recorded_at", "-pk"]

    def __str__(self):
        return f"{self.get_event_type_display()} — {self.contact}"

    def clean(self):
        super().clean()
        if not self.source.strip():
            raise ValidationError({"source": "Informe onde o consentimento ou descadastro foi recebido."})
        if not self.evidence.strip():
            raise ValidationError({"evidence": "Registre a evidência da solicitação."})

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Eventos são registros históricos; crie um novo evento para corrigir o estado.")
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Eventos históricos não podem ser apagados pela aplicação.")
