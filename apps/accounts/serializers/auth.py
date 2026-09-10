from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .user import UserSerializer


class LoginSerializer(TokenObtainPairSerializer):
    """
    Tizimga kirish serializeri — `phone_number` va `password` qabul qiladi.

    `USERNAME_FIELD` (`phone_number`) SimpleJWT tomonidan avtomatik olinadi.
    Javobga `access`, `refresh` bilan birga `user` ma'lumoti ham qo'shiladi.
    Nofaol (`is_active=False`) foydalanuvchi SimpleJWT tomonidan rad etiladi.
    """

    @classmethod
    def get_token(cls, user):
        """Token ichiga frontend uchun qulay claim'larni qo'shadi."""
        token = super().get_token(user)
        token["full_name"] = user.full_name
        token["role_id"] = str(user.role_id) if user.role_id else None
        token["branch_id"] = str(user.branch_id) if user.branch_id else None
        return token

    def validate(self, attrs):
        """Standart tekshiruvdan so'ng javobga `user` obyektini qo'shadi."""
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user, context=self.context).data
        return data
