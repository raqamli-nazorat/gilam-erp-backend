from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import User


class UserSerializer(BaseModelSerializer):
    """
    Foydalanuvchi uchun serializer.

    `password` faqat yozish uchun; yaratish/yangilashda hash qilib saqlanadi.
    `role` va `branch` yoziladi, `role_info` / `branch_info` nested qaytadi.
    """

    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "phone_number",
            "password",
            "role",
            "branch",
            "is_staff",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "role": {"fields": ["id", "name"]},
            "branch": {"fields": ["id", "name"]},
        }

    def __init__(self, *args, **kwargs):
        """Yangilash (PATCH/PUT) so'rovlarida `password` majburiy bo'lmaydi."""
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["password"].required = False

    def create(self, validated_data):
        """Yangi foydalanuvchi yaratadi va parolni hash qilib saqlaydi."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Foydalanuvchini yangilaydi; parol berilgan bo'lsa qayta hash qilinadi."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password", "updated_at"])
        return user
