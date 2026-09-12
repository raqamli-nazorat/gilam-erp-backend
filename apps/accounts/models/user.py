from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from apps.base.models import BaseModel, BaseQuerySet

from .role import Role


class UserManager(BaseUserManager.from_queryset(BaseQuerySet)):

    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon raqami majburiy")

        org = extra_fields.pop("organization", None)
        branch = extra_fields.pop("branch", None)
        employee = extra_fields.get("employee")

        if org and not employee:
            from apps.hr.models import Employee

            employee = Employee.objects.create(
                organization=org,
                branch=branch,
                full_name=extra_fields.get("full_name", ""),
                phone_number=phone_number,
            )
            extra_fields["employee"] = employee

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo'lishi kerak")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo'lishi kerak")

        return self.create_user(phone_number, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):

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
    employee = models.OneToOneField(
        "hr.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_account",
        db_index=True,
        verbose_name="Xodim",
        help_text="Biriktirilgan kadrlar xodimi",
    )

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
        return f"{self.full_name} ({self.phone_number})"

    @property
    def organization(self):
        return self.employee.organization if self.employee else None

    @property
    def organization_id(self):
        return self.employee.organization_id if self.employee else None

    @property
    def branch(self):
        return self.employee.branch if self.employee else None

    @property
    def branch_id(self):
        return self.employee.branch_id if self.employee else None

    @property
    def is_system_admin(self):
        return self.organization_id is None

    def get_role_permissions(self):
        if not self.role_id:
            return set()
        if not hasattr(self, "_role_perm_cache"):
            perms = self.role.permissions.values_list(
                "content_type__app_label", "codename"
            )
            self._role_perm_cache = {f"{app}.{code}" for app, code in perms}
        return self._role_perm_cache

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        if self.role_id and perm in self.get_role_permissions():
            return True
        if self.is_system_admin and not self.role_id:
            return True
        return super().has_perm(perm, obj)

    def get_accessible_branches(self, include_inactive=False):
        from apps.organization.models import Branch

        manager = Branch.objects.all() if include_inactive else Branch.objects.active()
        if self.is_system_admin:
            return manager

        branch_ids = set()
        if self.role and self.role.branches.exists():
            branches_qs = (
                self.role.branches.all()
                if include_inactive
                else self.role.branches.filter(is_active=True)
            )
            branch_ids.update(branches_qs.values_list("id", flat=True))
        if self.branch_id:
            branch_ids.add(self.branch_id)

        if branch_ids:
            return manager.filter(id__in=branch_ids)

        if self.organization_id:
            return manager.filter(
                organization_id=self.organization_id
            )

        return Branch.objects.none()

