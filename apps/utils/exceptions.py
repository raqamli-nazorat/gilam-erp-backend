"""
API xatoliklarini qayta ishlash va moslashtirilgan javoblar berish uchun utilitlar.

Ushbu modul Django va DRF validatsiya xatoliklarini unifikatsiyalangan javob
formatiga o'tkazish hamda standart HTTP xatolik handlerlarini ta'minlaydi.
"""

import logging

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import JsonResponse

from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as base_exception_handler
from rest_framework.views import set_rollback

logger = logging.getLogger("api.errors")

SERVER_ERROR_MSG = "Serverdagi ichki xatolik."


def exception_handler(exc, context):
    """
    DRF uchun maxsus xatoliklarni ushlab qoluvchi (custom exception handler) funksiya.

    Args:
        exc (Exception): Yuzaga kelgan xatolik obyekti.
        context (dict): Xatolik yuzaga kelgan kontekst (request, view va h.k.).

    Returns:
        Response | JsonResponse | None: Unifikatsiyalangan xatolik javob formati.
    """
    if isinstance(exc, DjangoValidationError):
        exc = _convert_django_validation_error(exc)

    response = base_exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            response.data.setdefault("_error_code", _extract_error_code(exc))
        return response

    if settings.DEBUG:
        return None

    request = context.get("request")
    logger.error(
        "Unhandled API exception: %s %s",
        getattr(request, "method", "-"),
        getattr(request, "path", "-"),
        exc_info=exc,
    )

    set_rollback()

    return Response(
        {
            "detail": SERVER_ERROR_MSG,
            "_is_friendly": False,
            "_error_code": "server_error",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _convert_django_validation_error(exc):
    """
    DjangoValidationError obyektini DRF ValidationError obyektiga o'tkazadi.

    Args:
        exc (DjangoValidationError): Django modeli yoki validatsiyasidan chiqqan xatolik.

    Returns:
        DRFValidationError: DRF formatidagi validatsiya xatosi.
    """
    if hasattr(exc, "message_dict"):
        return DRFValidationError(detail=exc.message_dict)
    return DRFValidationError(detail=exc.messages)


def _extract_error_code(exc):
    """
    Xatolik obyektidan xatolik kodini (error_code) ajratib oladi.

    Args:
        exc (Exception): Xatolik obyekti.

    Returns:
        str: Xatolik kodi matni.
    """
    code = getattr(exc, "default_code", None)
    return str(code) if code else "error"


def _error_response(status_code, message, error_code, is_friendly=True):
    """
    Standartlashtirilgan JSON xatolik javobini yaratadi.

    Args:
        status_code (int): HTTP status kodi.
        message (str): Foydalanuvchiga ko'rsatiladigan xabar.
        error_code (str): Xatolikning unikal kodi.
        is_friendly (bool, optional): Foydalanuvchiga ko'rsatishga mosligi. Defaults to True.

    Returns:
        JsonResponse: Tayyor xatolik strukturasi bilan JSON javob.
    """
    return JsonResponse(
        {
            "data": None,
            "error": {
                "errorId": status_code,
                "errorCode": error_code,
                "isFriendly": is_friendly,
                "errorMsg": message,
                "details": None,
            },
            "success": False,
        },
        status=status_code,
        json_dumps_params={"ensure_ascii": False},
    )


def handler400(request, exception=None, *args, **kwargs):
    """
    400 Bad Request xatosi uchun ishlovchi handler.
    """
    return _error_response(
        status.HTTP_400_BAD_REQUEST,
        "Noto'g'ri so'rov.",
        "bad_request",
    )


def handler403(request, exception=None, *args, **kwargs):
    """
    403 Forbidden xatosi uchun ishlovchi handler.
    """
    return _error_response(
        status.HTTP_403_FORBIDDEN,
        "Ushbu amal uchun ruxsat yo'q.",
        "permission_denied",
    )


def handler404(request, exception=None, *args, **kwargs):
    """
    404 Not Found xatosi uchun ishlovchi handler.
    """
    return _error_response(
        status.HTTP_404_NOT_FOUND,
        "Sahifa topilmadi.",
        "not_found",
    )


def handler500(request, *args, **kwargs):
    """
    500 Internal Server Error xatosi uchun ishlovchi handler.
    """
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        SERVER_ERROR_MSG,
        "server_error",
        is_friendly=False,
    )

