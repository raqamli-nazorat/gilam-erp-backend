from apps.base.serializers import BaseModelSerializer

from ..models import DesignPhoto


class DesignPhotoSerializer(BaseModelSerializer):
    """Dizayn fotosurati uchun serializer."""

    class Meta:
        model = DesignPhoto
        fields = [
            "id",
            "photo_path",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
