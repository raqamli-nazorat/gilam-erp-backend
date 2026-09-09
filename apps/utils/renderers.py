"""
API javoblarini unifikatsiyalangan standart formatga o'tkazuvchi custom renderers.

Muvaffaqiyatli hamda xatolik bilan yakunlangan barcha javoblar:
{"data": ..., "error": ..., "success": true/false} shaklida qaytariladi.
"""

from rest_framework.renderers import JSONRenderer

DEFAULT_VALIDATION_MSG = "Ma'lumotlarni tekshirishda xatolik yuzaga keldi."
DEFAULT_SERVER_MSG = "Serverdagi ichki xatolik."
DEFAULT_ERROR_MSG = "Kutilmagan xatolik yuzaga keldi."

SCHEMA_VIEW_MODULES = ("drf_spectacular", "drf_yasg", "rest_framework.schemas")


class ResponseRenderer(JSONRenderer):
    """
    Barcha API javoblarini unifikatsiyalangan standart strukturaga o'rab beruvchi renderer.

    - Muvaffaqiyatli javoblar: {"data": data, "error": None, "success": True}
    - Xatolik javoblari: {"data": None, "error": {...}, "success": False}
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Ma'lumotlarni render qiladi va javobni umumiy API formatiga moslaydi.

        Args:
            data (Any): View tomonidan qaytarilgan ma'lumotlar payload'i.
            accepted_media_type (str, optional): Media turi.
            renderer_context (dict, optional): Context ma'lumotlari.

        Returns:
            bytes: JSON formatga aylantirilgan baytlar.
        """
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        status_code = getattr(response, "status_code", 200)

        if self._is_schema_view(renderer_context):
            return super().render(data, accepted_media_type, renderer_context)

        if status_code == 204:
            return super().render(data, accepted_media_type, renderer_context)

        if status_code < 400:
            wrapped = {"data": data, "error": None, "success": True}
            return super().render(wrapped, accepted_media_type, renderer_context)

        wrapped = {
            "data": None,
            "error": self._build_error(data, status_code),
            "success": False,
        }
        return super().render(wrapped, accepted_media_type, renderer_context)

    @staticmethod
    def _is_schema_view(renderer_context):
        """
        Joriy so'rov Swagger/OpenAPI dokumentatsiya view'si ekanligini aniqlaydi.

        Args:
            renderer_context (dict): Context ma'lumotlari.

        Returns:
            bool: Schema view bo'lsa True, aks holda False.
        """
        view = renderer_context.get("view")
        if view is None:
            return False
        module = type(view).__module__ or ""
        return module.startswith(SCHEMA_VIEW_MODULES)

    def _build_error(self, data, status_code):
        """
        Xatolik javoblari uchun unifikatsiyalangan error strukturasini quradi.

        Args:
            data (Any): Xatolik ma'lumoti.
            status_code (int): HTTP status kodi.

        Returns:
            dict: Standart error ob'ekti.
        """
        is_friendly = True
        error_code = None

        if isinstance(data, dict):
            data = dict(data)
            is_friendly = bool(data.pop("_is_friendly", True))
            error_code = data.pop("_error_code", None)

        error_msg, details = self._parse_error_payload(data, status_code)

        if status_code >= 500:
            is_friendly = False

        return {
            "errorId": status_code,
            "errorCode": str(error_code) if error_code else None,
            "isFriendly": is_friendly,
            "errorMsg": str(error_msg),
            "details": details,
        }

    @staticmethod
    def _parse_error_payload(data, status_code):
        """
        Xatolik payload'ini tahlil qilib, errorMsg va details'ni ajratib beradi.

        Args:
            data (Any): Xatolik ma'lumotlari.
            status_code (int): HTTP status kodi.

        Returns:
            tuple[str, Any]: (error_msg, details) juftligi.
        """
        if isinstance(data, dict):
            if "detail" in data:
                detail = data.pop("detail")

                if isinstance(detail, dict):
                    data.update(detail)
                    return DEFAULT_VALIDATION_MSG, (data or None)
                if isinstance(detail, (list, tuple)):
                    data["non_field_errors"] = list(detail)
                    return DEFAULT_VALIDATION_MSG, (data or None)

                return detail, (data or None)

            return DEFAULT_VALIDATION_MSG, (data or None)

        if isinstance(data, (list, tuple)):
            items = list(data)
            if any(isinstance(item, dict) for item in items):
                return DEFAULT_VALIDATION_MSG, {"items": items}
            return DEFAULT_VALIDATION_MSG, {"non_field_errors": items}

        if isinstance(data, str):
            return data, None

        if status_code >= 500:
            return DEFAULT_SERVER_MSG, None

        return DEFAULT_ERROR_MSG, None

