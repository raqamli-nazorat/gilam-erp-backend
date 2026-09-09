"""
Ruxsatlarni (permissions) tekshiruvchi bazaviy klasslar.

Ushbu modul Django model ruxsatlarini to'liq (GET metodini ham o'z ichiga olgan holda)
hamda obyekt egasi/xodimlarni (IsOwnerOrStaff) tekshirish mexanizmlarini taqdim etadi.
"""

from rest_framework import permissions


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    """
    DjangoModelPermissions klassining kengaytirilgan varianti.

    Standart DjangoModelPermissions GET so'rovlari uchun view ruxsatini
    tekshirmaydi. Ushbu klass GET so'rovlariga ham '%(app_label)s.view_%(model_name)s'
    ruxsatini majburiy etib belgilaydi.
    """

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class IsOwnerOrStaff(permissions.BasePermission):
    """
    So'rov yuboruvchi foydalanuvchi obyekt egasi yoki xodim (staff/superuser)
    ekanligini tekshiruvchi permission klassi.
    """

    def has_object_permission(self, request, view, obj):
        """
        Obyekt darajasidagi ruxsatni tekshiradi.

        Args:
            request (Request): DRF request obyekti.
            view (APIView): Ishga tushirilayotgan view.
            obj (Model): Tekshirilayotgan model obyekti.

        Returns:
            bool: Ruxsat berilgan bo'lsa True, aks holda False.
        """
        if request.user.is_staff or request.user.is_superuser:
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user

        return obj == request.user


