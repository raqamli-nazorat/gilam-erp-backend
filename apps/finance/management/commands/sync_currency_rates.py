"""Markaziy bank kursini olib, bazadagi valyutalar uchun saqlaydi (cron uchun)."""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from rest_framework.exceptions import APIException

from apps.finance.services.currency import sync_ledgers


class Command(BaseCommand):
    help = "Bugungi Markaziy bank valyuta kurslarini bazaga saqlaydi"

    def handle(self, *args, **options):
        """Bugungi kursni sinxronlaydi; xatolikda noldan farqli kod bilan tugaydi."""
        day = timezone.localdate()
        try:
            ledgers = sync_ledgers(day)
        except APIException as exc:
            raise CommandError(f"Kurs olinmadi ({day}): {exc.detail}") from exc
        self.stdout.write(
            self.style.SUCCESS(f"{day}: {len(ledgers)} ta valyuta kursi saqlandi")
        )
