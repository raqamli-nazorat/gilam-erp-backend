from apps.base.serializers import BaseModelSerializer

from ..models import EmployeeLedger


class EmployeeLedgerSerializer(BaseModelSerializer):

    class Meta:
        model = EmployeeLedger
        fields = [
            "id",
            "branch",
            "employee",
            "type",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
            "employee": {"fields": ["id", "full_name", "phone_number"]},
        }
