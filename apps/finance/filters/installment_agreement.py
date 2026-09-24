import django_filters

from apps.base.filters import UUIDInFilter

from ..models import InstallmentAgreement


class InstallmentAgreementFilter(django_filters.FilterSet):
    agreement_number = django_filters.CharFilter(lookup_expr="icontains")
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    customer = UUIDInFilter(field_name="customer_id", lookup_expr="in")
    order = UUIDInFilter(field_name="order_id", lookup_expr="in")
    status = django_filters.ChoiceFilter(choices=InstallmentAgreement.Status.choices)
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = InstallmentAgreement
        fields = [
            "agreement_number",
            "organization",
            "customer",
            "order",
            "status",
            "start_date",
            "end_date",
        ]
