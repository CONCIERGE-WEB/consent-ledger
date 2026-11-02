from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import ConsentEvent, Contact


class ConsentLedgerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="operator",
            email="operator@example.test",
            password="A-long-test-password-2026",
        )
        self.contact = Contact.objects.create(phone="+5511999999999", name="Cliente")

    def test_phone_must_be_in_e164_format(self):
        contact = Contact(phone="11999999999")
        with self.assertRaises(ValidationError):
            contact.full_clean()

    def test_consent_evidence_is_required(self):
        event = ConsentEvent(
            contact=self.contact,
            event_type=ConsentEvent.EventType.OPTED_IN,
            source="",
            evidence="",
        )
        with self.assertRaises(ValidationError):
            event.save()

    def test_events_are_append_only(self):
        event = ConsentEvent.objects.create(
            contact=self.contact,
            event_type=ConsentEvent.EventType.OPTED_IN,
            source="Formulário do site",
            evidence="Checkbox marcado em 2026-10-01",
            recorded_by=self.user,
        )
        with self.assertRaises(ValidationError):
            event.save()
        with self.assertRaises(ValidationError):
            event.delete()

    def test_health_endpoint_exposes_no_contact_data(self):
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_admin_requires_authentication(self):
        response = self.client.get("/admin/ledger/contact/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_repeated_login_failures_are_temporarily_blocked(self):
        for _ in range(5):
            self.client.post(
                "/admin/login/",
                {"username": "operator", "password": "incorrect-password"},
            )
        response = self.client.post(
            "/admin/login/",
            {"username": "operator", "password": "A-long-test-password-2026"},
        )
        self.assertEqual(response.status_code, 429)

    def test_latest_opt_out_overrides_prior_opt_in(self):
        ConsentEvent.objects.create(
            contact=self.contact,
            event_type=ConsentEvent.EventType.OPTED_IN,
            source="Formulário do site",
            evidence="Checkbox marcado",
            recorded_by=self.user,
        )
        ConsentEvent.objects.create(
            contact=self.contact,
            event_type=ConsentEvent.EventType.OPTED_OUT,
            source="Solicitação do titular",
            evidence="Mensagem de descadastro recebida",
            recorded_by=self.user,
        )
        self.client.force_login(self.user)
        response = self.client.get("/admin/ledger/contact/")
        self.assertContains(response, "Descadastrado")
