import django_filters

from apps.base.filters import UUIDInFilter

from ..models import Payment


class PaymentFilter(django_filters.FilterSet):
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    order = UUIDInFilter(field_name="order_id", lookup_expr="in")
    installment_agreement = UUIDInFilter(
        field_name="installment_agreement_id", lookup_expr="in"
    )
    customer = UUIDInFilter(field_name="customer_id", lookup_expr="in")
    payment_method = django_filters.ChoiceFilter(choices=Payment.PaymentMethod.choices)
    payment_type = django_filters.ChoiceFilter(choices=Payment.PaymentType.choices)
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Payment
        fields = [
            "organization",
            "order",
            "installment_agreement",
            "customer",
            "payment_method",
            "payment_type",
            "start_date",
            "end_date",
        ]
