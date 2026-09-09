"""
Barcha loyiha modellari uchun bazaviy model va QuerySet klasslari.

Ushbu modul UUID identifikatorlari, soft-delete mexanizmi, created_at/updated_at
va avtomatik tartiblash (ordering) funksionalligini ta'minlaydi.
"""

import uuid

from django.db import models
from django.db.models.base import ModelBase


class BaseQuerySet(models.QuerySet):
    """
    Barcha modellar uchun umumiy QuerySet kengaytmasi.

    Faqat aktiv obyektlarni saralash hamda soft-delete / hard-delete
    operatsiyalarini bajarish metodlarini o'z ichiga oladi.
    """

    def active(self):
        """Faqat aktiv bo'lgan obyektlar to'plamini qaytaradi (`is_active=True`)."""
        return self.filter(is_active=True)

    def inactive(self):
        """Faqat nofaol (yo'q qilingan) obyektlar to'plamini qaytaradi (`is_active=False`)."""
        return self.filter(is_active=False)

    def delete(self):
        """Obyektlarni bazadan o'chirmasdan, ularni soft-delete qiladi (`is_active=False`)."""
        return self.update(is_active=False)

    def hard_delete(self):
        """Obyektlarni ma'lumotlar bazasidan butunlay o'chirib yuboradi."""
        return super().delete()


class BaseModelMeta(ModelBase):
    """
    BaseModel uchun metaklass.

    Model yaratilishida agarda `ordering` belgilanmagan bo'lsa,
    standart bo'yicha `['-created_at']` bo'yicha tartiblashni o'rnatadi.
    """

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        if hasattr(new_class, "_meta") and not new_class._meta.abstract:
            if not new_class._meta.ordering:
                new_class._meta.ordering = ["-created_at"]
        return new_class


class BaseModel(models.Model, metaclass=BaseModelMeta):
    """
    Loyihadagi barcha modellar uchun bazaviy abstrakt model.

    Maydonlar:
        - id: UUID v4 unikal identifikatori.
        - is_active: Obyekt aktivlik holati (soft-delete uchun).
        - created_at: Yaratilgan vaqti.
        - updated_at: Oxirgi marta yangilangan vaqti.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(
        default=True, db_index=True, verbose_name="Is Active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="Yaratilgan vaqti"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def delete(self, *args, **kwargs):
        """Obyektni bazadan o'chirmasdan `is_active=False` holatiga o'tkazadi (Soft Delete)."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def hard_delete(self, *args, **kwargs):
        """Obyektni ma'lumotlar bazasidan butunlay o'chiradi."""
        super().delete(*args, **kwargs)
