from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import DesignPhotoFilter
from ..models import DesignPhoto
from ..serializers import DesignPhotoSerializer


class DesignPhotoViewSet(BaseManageViewSet):
    """Dizayn fotosuratlari uchun CRUD ViewSet."""

    queryset = DesignPhoto.objects.active()
    serializer_class = DesignPhotoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DesignPhotoFilter
    search_fields = ["name", "description", "photo_path"]
    ordering_fields = ["name", "created_at"]
