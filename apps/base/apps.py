"""
Base ilovasi konfiguratsiyasi va signallarni ulash.

Ushbu modul BaseModel'dan meros olgan modellarni avtomatik
auditlog reyestridan o'tkazishni ta'minlaydi.
"""

from django.apps import AppConfig, apps
from django.db.models.signals import class_prepared


def register_auditlog(sender, **kwargs):
    """
    Model tayyor bo'lganda (class_prepared signali kelganda) agar u BaseModel subklassi bo'lsa,
    uni auditlog reyestriga ro'yxatga oladi.

    Args:
        sender (type[Model]): Tayyor bo'lgan Django modeli klassi.
    """
    from auditlog.registry import auditlog

    from apps.base.models import BaseModel

    if issubclass(sender, BaseModel) and not sender._meta.abstract:
        try:
            auditlog.register(sender)
        except Exception:
            pass


class BaseConfig(AppConfig):
    """Base ilovasi konfiguratsiya klassi."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.base"
    verbose_name = "Baza"

    def ready(self):
        """
        Ilova tayyor bo'lganda auditlog ro'yxatga olish signal va modellarni initsializatsiya qiladi.
        """
        class_prepared.connect(register_auditlog)

        from auditlog.registry import auditlog

        from apps.base.models import BaseModel

        for model in apps.get_models():
            if issubclass(model, BaseModel) and not model._meta.abstract:
                try:
                    auditlog.register(model)
                except Exception:
                    pass
