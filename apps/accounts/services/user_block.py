from ..models import UserBlockLog


def get_latest_block_log(user):
    """Foydalanuvchining eng oxirgi bloklash/blokdan chiqarish yozuvini qaytaradi."""
    return user.block_logs.order_by("-created_at").first()


def is_user_blocked(user) -> bool:
    """Foydalanuvchi joriy holatda bloklanganmi yo'qmi tekshiradi."""
    latest = get_latest_block_log(user)
    return bool(latest and latest.type == UserBlockLog.Type.BLOCK)
