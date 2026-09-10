"""
API so'rovlarini cheklash (throttling) uchun moslashtirilgan klasslar va mixinlar.

Ushbu modul moslashuvchan rate-limit formatlarini qo'llab-quvvatlaydi va
throttling chegarasidan oshganda mos javob berish mexanizmini ta'minlaydi.
"""

import hashlib
import logging
import re

from rest_framework.exceptions import Throttled
from rest_framework.throttling import ScopedRateThrottle

logger = logging.getLogger("api.throttling")

RATE_RE = re.compile(r"^(\d+)/(\d+)?([smhd])[a-z]*$")
UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


class CustomScopedRateThrottle(ScopedRateThrottle):
    """
    Maxsus kengaytirilgan ScopedRateThrottle klassi.

    Moslashuvchan tezlik formatlarini (masalan, '5/3m', '10/12h') qo'llab-quvvatlaydi
    hamda foydalanuvchi yoki IP bo'yicha kesh kalitlarini shakllantiradi.
    """

    def parse_rate(self, rate):
        """
        Berilgan tezlik matnini (rate string) tahlil qilib, so'rovlar soni va soniyalardagi davomiylikni qaytaradi.

        Args:
            rate (str): '5/m', '3/3m', '10/12h' ko'rinishidagi tezlik chegarasi.

        Returns:
            tuple[int|None, int|None]: (num_requests, duration) ko'rinishidagi juftlik.
        """
        if rate is None:
            return (None, None)

        match = RATE_RE.match(str(rate).strip().lower())
        if not match:
            raise ValueError(
                f"Throttle formati noto'g'ri kiritilgan: {rate!r}. "
                "To'g'ri format: 'son/birlik' yoki 'son/Xbirlik' "
                "(masalan: '5/m', '3/3m', '10/12h')"
            )

        num_requests = int(match.group(1))
        multiplier = int(match.group(2)) if match.group(2) else 1
        duration = UNITS[match.group(3)] * multiplier

        if num_requests < 1 or duration < 1:
            raise ValueError(f"Throttle qiymatlari musbat bo'lishi kerak: {rate!r}")

        return (num_requests, duration)

    def get_cache_key(self, request, view):
        """
        Throttling holatini saqlash uchun kesh kalitini shakllantiradi.

        Args:
            request (Request): DRF request obyekti.
            view (APIView): Ishga tushirilayotgan view.

        Returns:
            str | None: Kesh kaliti yoki throttling qo'llanmasa None.
        """
        if not getattr(self, "scope", None) and hasattr(self, "scope_attr"):
            self.scope = getattr(view, self.scope_attr, None)

        if not self.scope:
            return None

        if self.scope == "login":
            ident = self._login_ident(request)
        elif request.user and request.user.is_authenticated:
            ident = f"user:{request.user.pk}"
        else:
            ident = f"ip:{self.get_ident(request)}"

        ident = hashlib.sha256(ident.encode("utf-8")).hexdigest()

        return self.cache_format % {"scope": self.scope, "ident": ident}

    def _login_ident(self, request):
        """
        Tizimga kirish (login) so'rovlari uchun unikal identifikator hosil qiladi.

        Args:
            request (Request): DRF request obyekti.

        Returns:
            str: Login identifikator matni.
        """
        try:
            phone_number = str(request.data.get("phone_number") or "").strip()
        except Exception:
            phone_number = ""
        return f"login:{self.get_ident(request)}:{phone_number}"


class ThrottleExceptionHandlerMixin:
    """
    View'lar uchun throttling xatoliklarini qayta ishlovchi va qolgan urinishlar
    sonini hisoblab beruvchi mixin.
    """

    def handle_exception(self, exc):
        """
        Yuzaga kelgan istisno (exception)ni ushlaydi va throttling bo'yicha qo'shimcha ma'lumotlarni qo'shadi.

        Args:
            exc (Exception): Yuzaga kelgan exception obyekti.

        Returns:
            Response: DRF Response obyekti.
        """
        response = super().handle_exception(exc)

        if response is None or not isinstance(response.data, dict):
            return response

        if isinstance(exc, Throttled):
            wait = int(exc.wait or 0)
            response.data["detail"] = (
                f"Urinishlar soni tugadi. "
                f"Iltimos {wait} soniyadan so'ng qayta urinib ko'ring."
            )
            response.data["retry_after_seconds"] = wait
            response.data["attempts_left"] = 0
        elif response.status_code in (400, 401):
            attempts_left = self._get_attempts_left()
            if attempts_left is not None:
                response.data["attempts_left"] = attempts_left

        return response

    def _get_attempts_left(self):
        """
        Joriy so'rov yuboruvchi uchun qolgan urinishlar (attempts_left) sonini hisoblaydi.

        Returns:
            int | None: Qolgan urinishlar soni yoki hisoblab bo'lmasa None.
        """
        try:
            for throttle in self.get_throttles():
                if not isinstance(throttle, ScopedRateThrottle):
                    continue

                throttle.scope = getattr(self, throttle.scope_attr, None)
                if not throttle.scope:
                    continue

                num_requests, duration = throttle.parse_rate(throttle.get_rate())
                if not num_requests or not duration:
                    continue

                cache_key = throttle.get_cache_key(self.request, view=self)
                if not cache_key:
                    continue

                history = throttle.cache.get(cache_key, [])
                now = throttle.timer()
                recent = [t for t in history if t > now - duration]

                return max(0, num_requests - len(recent))
        except Exception:
            logger.warning("attempts_left hisoblashda xatolik", exc_info=True)

        return None
