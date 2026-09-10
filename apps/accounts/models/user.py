from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from apps.base.models import BaseModel, BaseQuerySet

from .role import Role


class UserManager(BaseUserManager.from_queryset(BaseQuerySet)):
    """
    User modeli uchun maxsus manager.

    `BaseQuerySet` dan `active()` / `inactive()` va soft-delete metodlarini,
    `BaseUserManager` dan `create_user` / `create_superuser` ni meros oladi.
    """

    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        """Telefon raqami va parol bilan oddiy foydalanuvchi yaratadi."""
        if not phone_number:
            raise ValueError("Telefon raqami majburiy")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """To'liq huquqli superuser yaratadi."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo'lishi kerak")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo'lishi kerak")

        return self.create_user(phone_number, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Tizim foydalanuvchisi — phone_number orqali tizimga kiradi."""

    full_name = models.CharField(max_length=255, verbose_name="F.I.Sh.")
    phone_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Telefon raqami",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Rol",
    )
    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Filial",
    )
    # Django admin panelga kirish uchun — BaseModel dagi 4 maydondan tashqari
    is_staff = models.BooleanField(
        default=False, verbose_name="Xodim (admin panelga kirish)"
    )

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        """Foydalanuvchi F.I.Sh. va telefon raqamini qaytaradi."""
        return f"{self.full_name} ({self.phone_number})"
