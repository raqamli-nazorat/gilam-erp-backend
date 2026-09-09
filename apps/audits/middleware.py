"""
JWT autentifikatsiyasi bilan ishlovchi Auditlog middleware.

DRF SimpleJWT tokeni orqali request.user ni middleware darajasida aniqlaydi,
shu sababli auditlog harakatlariga foydalanuvchi (actor/user) to'g'ri biriktiriladi
va 'system' bo'lib qolmaydi.
"""

from auditlog.middleware import AuditlogMiddleware
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuditlogMiddleware(AuditlogMiddleware):
    """
    Standard AuditlogMiddleware sinfini kengaytirgan holda,
    JWT header (Authorization: Bearer <token>) bo'yicha foydalanuvchini (request.user)
    middleware bosqichida aniqlaydi va biriktiradi.
    """

    def __call__(self, request):
        if (
                not hasattr(request, "user")
                or not request.user
                or request.user.is_anonymous
        ):
            try:
                authenticator = JWTAuthentication()
                auth_result = authenticator.authenticate(request)
                if auth_result is not None:
                    user, _ = auth_result
                    request.user = user
            except Exception:
                pass

        return super().__call__(request)
