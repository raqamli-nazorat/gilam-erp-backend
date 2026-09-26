"""Finance app'ning fon vazifalari (Celery)."""

from celery import shared_task

from .services.currency import BankUnavailable, sync_ledgers


@shared_task(
    autoretry_for=(BankUnavailable,),
    retry_backoff=300,
    retry_backoff_max=1800,
    retry_kwargs={"max_retries": 6},
)
def sync_currency_rates() -> int:
    """Bugungi Markaziy bank kursini olib saqlaydi; bank ishlamasa qayta urinadi."""
    return len(sync_ledgers())
