from decimal import Decimal
from typing import Any

from django.db.models import DecimalField
from django_stubs_ext import StrPromise


def _decimal_field(
    verbose_name: StrPromise,
    *,
    max_digits: int,
    decimal_places: int,
    nullable: bool = False,
    **kwargs: Any,
):
    options: dict[str, Any] = {
        "verbose_name": verbose_name,
        "max_digits": max_digits,
        "decimal_places": decimal_places,
    }

    if nullable:
        options.update(blank=True, null=True)
    else:
        options["default"] = Decimal(0)

    options.update(kwargs)
    return DecimalField(**options)


def money_field(
    verbose_name: StrPromise,
    *,
    max_digits: int,
    nullable: bool = False,
    **kwargs: Any,
):
    """Создать DecimalField для денежного значения."""
    return _decimal_field(
        verbose_name,
        max_digits=max_digits,
        decimal_places=2,
        nullable=nullable,
        **kwargs,
    )


def price_field(verbose_name: StrPromise, *, nullable: bool = False, **kwargs: Any):
    """Создать DecimalField для цены до 99 999.99."""
    return money_field(verbose_name, max_digits=7, nullable=nullable, **kwargs)


def expense_field(verbose_name: StrPromise, *, nullable: bool = False, **kwargs: Any):
    """Создать DecimalField для расходов до 99 999 999.99."""
    return money_field(verbose_name, max_digits=10, nullable=nullable, **kwargs)
