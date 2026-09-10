"""
Ma'lumotlar va fayllarni tekshirish (validation) uchun maxsus validatorlar.

Ushbu modul telefon raqamlari, murakkab parollar va fayl hajmini
tekshiruvchi validatorlarni o'z ichiga oladi.
"""

import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

# O'zbekiston telefon raqamlari formati uchun validator (+998XXXXXXXXX)
phone_validator = RegexValidator(
    regex=r"^\+998\d{9}$",
    message="Telefon raqami noto'g'ri formatda kiritildi. Kutilgan format: '+9989012345678'. Uzunligi aynan 13 ta belgi bo'lishi shart.",
)


class ComplexPasswordValidator:
    """
    Parol xavfsizligi va murakkabligini tekshiruvchi validator.

    Parolda kamida bitta katta harf, kichik harf, raqam va maxsus belgi
    mavjudligini talab qiladi.
    """

    def validate(self, password, user=None):
        """
        Parolni xavfsizlik talablariga mosligini tekshiradi.

        Args:
            password (str): Tekshirilayotgan parol.
            user (User, optional): Foydalanuvchi ob'ekti.

        Raises:
            ValidationError: Parol talablarga javob bermasa tashlanadi.
        """
        if not re.findall(r"[A-Z]", password):
            raise ValidationError(
                "Parol kamida bitta katta harf (A-Z) ni o'z ichiga olishi kerak.",
                code="password_no_upper",
            )
        if not re.findall(r"[a-z]", password):
            raise ValidationError(
                "Parol kamida bitta kichik harf (a-z) ni o'z ichiga olishi kerak.",
                code="password_no_lower",
            )
        if not re.findall(r"\d", password):
            raise ValidationError(
                "Parol kamida bitta raqam (0-9) ni o'z ichiga olishi kerak.",
                code="password_no_number",
            )
        if not re.findall(r"[^A-Za-z0-9]", password):
            raise ValidationError(
                "Parol kamida bitta maxsus belgi (@, #, $, %, vb.) ni o'z ichiga olishi kerak.",
                code="password_no_symbol",
            )

    def get_help_text(self):
        """
        Foydalanuvchilar uchun parol bo'yicha yordamchi matnni qaytaradi.

        Returns:
            str: Yordamchi matn.
        """
        return "Parolingiz kamida bitta katta harf, bitta kichik harf, bitta raqam va bitta maxsus belgi saqlashi kerak."


@deconstructible
class FileSizeValidator:
    """
    Yuklanayotgan fayl hajmini megabaytlarda cheklovchi validator.
    """

    def __init__(self, max_size_mb):
        """
        Validator parametrlarini initsializatsiya qiladi.

        Args:
            max_size_mb (int | float): Maksimal ruxsat etilgan fayl hajmi (MB).
        """
        self.max_size_mb = max_size_mb

    def __call__(self, file):
        """
        Fayl hajmini maksimal hajm bilan solishtiradi.

        Args:
            file (UploadedFile): Yuklanayotgan fayl ob'ekti.

        Raises:
            ValidationError: Fayl hajmi ruxsat berilgan hajmdan katta bo'lsa.
        """
        if file.size > self.max_size_mb * 1024 * 1024:
            raise ValidationError(
                f"Fayl hajmi juda katta. Maksimal hajm {self.max_size_mb} MB bo'lishi ruxsat etiladi."
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and self.max_size_mb == other.max_size_mb
        )
