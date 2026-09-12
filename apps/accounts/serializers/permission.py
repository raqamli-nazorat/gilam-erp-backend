from django.contrib.auth.models import Permission
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):

    model_name = serializers.CharField(source="content_type.model", read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "model_name"]

    def get_name(self, obj):
        action = obj.codename.split("_")[0]
        model_name = obj.content_type.name.capitalize()

        mapping = {
            "add": f"{model_name} qo'shish",
            "change": f"{model_name} tahrirlash",
            "delete": f"{model_name} o'chirish",
            "view": f"{model_name} ko'rish",
        }
        return mapping.get(action, obj.name)
