"""Product data fetching and formatting services."""

from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict, List, Tuple, Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel

from ..core_client import APIClient
from ..client import ProductsAPIClient
from ..schemas import (
    Item,
    Commissions,
    Price,
    PriceIndexes,
    MarketingActions,
)
from ..i18n.ru_labels import ru_label


class Section(TypedDict):
    title: str
    rows: List[Tuple[str, str]]


def format_value(value: Any) -> str:
    """Format any value to string for display."""
    if value is None:
        return "—"
    elif isinstance(value, Decimal):
        return str(value.quantize(Decimal("0.01")))
    elif isinstance(value, bool):
        return "Да" if value else "Нет"
    elif isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return str(value)


def create_section_from_model(
    model: BaseModel, title: str, exclude_fields: Optional[set] = None
) -> Section:
    """Create a section from a Pydantic model."""
    exclude_fields = exclude_fields or set()
    rows = []

    model_data = model.model_dump()

    if hasattr(model, "__pydantic_computed_fields__"):
        for field_name in model.__pydantic_computed_fields__:
            if field_name not in exclude_fields:
                try:
                    value = getattr(model, field_name)
                    model_data[field_name] = value
                except Exception:
                    continue

    for field_name, value in model_data.items():
        if field_name not in exclude_fields and not isinstance(value, (dict, list)):
            try:
                label = ru_label(field_name)
                formatted_value = format_value(value)
                rows.append((label, formatted_value))
            except Exception:
                continue

    return Section(title=title, rows=rows)


def create_marketing_actions_section(marketing_actions: MarketingActions) -> Section:
    """Create marketing actions section with actions table."""
    rows = []

    # Add main fields
    if marketing_actions.current_period_from:
        rows.append(
            (
                ru_label("current_period_from"),
                format_value(marketing_actions.current_period_from),
            )
        )
    if marketing_actions.current_period_to:
        rows.append(
            (
                ru_label("current_period_to"),
                format_value(marketing_actions.current_period_to),
            )
        )

    rows.append(
        (
            ru_label("ozon_actions_exist"),
            format_value(marketing_actions.ozon_actions_exist),
        )
    )

    # Add actions summary
    if marketing_actions.actions:
        actions_summary = f"Количество акций: {len(marketing_actions.actions)}"
        rows.append(("Акции", actions_summary))

        # Add each action as a separate row
        for i, action in enumerate(marketing_actions.actions, 1):
            action_info = f"{action.title} ({format_value(action.value)}) {format_value(action.date_from)} - {format_value(action.date_to)}"
            rows.append((f"Акция {i}", action_info))
    else:
        rows.append(("Акции", "—"))

    return Section(title="Маркетинговые акции", rows=rows)


def create_price_indexes_section(price_indexes: PriceIndexes) -> List[Section]:
    """Create price indexes sections."""
    sections = []

    # Main price indexes section
    main_rows = [(ru_label("color_index"), format_value(price_indexes.color_index))]
    sections.append(Section(title="Индексы цен", rows=main_rows))

    # Sub-index sections
    if price_indexes.external_index_data:
        external_section = create_section_from_model(
            price_indexes.external_index_data, "Внешние данные индекса"
        )
        sections.append(external_section)

    if price_indexes.ozon_index_data:
        ozon_section = create_section_from_model(
            price_indexes.ozon_index_data, "Данные индекса Ozon"
        )
        sections.append(ozon_section)

    if price_indexes.self_marketplaces_index_data:
        self_section = create_section_from_model(
            price_indexes.self_marketplaces_index_data,
            "Данные индекса собственных маркетплейсов",
        )
        sections.append(self_section)

    return sections


async def fetch_product_data(
    sku: str,
    *,
    client: APIClient,
    user_purchase_price: Optional[Decimal] = None,
) -> Dict[str, Any]:
    """
    Fetch and format product data for UI display.

    Returns:
        Dict with 'sections' (list[Section]) and 'raw' (original data)
        Or 'error' field if something fails.
    """
    try:
        product_client = ProductsAPIClient(client)
        ozon_item: Item = await product_client.get_product_info(sku)
        sections = sections_from_item(ozon_item, user_purchase_price)
        return {"sections": sections, "raw": ozon_item}

    except Exception as e:
        return {"error": f"Ошибка получения данных: {type(e).__name__}: {str(e)}"}


def create_profit_section(item: Item, user_purchase_price: Decimal) -> Section:
    """Create profit calculation section."""
    marketing_seller_price = item.price.marketing_seller_price
    total_commission = item.fbs_total_commission
    profit = marketing_seller_price - total_commission - user_purchase_price

    # Calculate profit margin as percentage
    profit_margin = Decimal(0)
    if user_purchase_price > 0:
        profit_margin = (profit / user_purchase_price * 100).quantize(Decimal("0.01"))

    rows = [
        (ru_label("user_purchase_price"), format_value(user_purchase_price)),
        (ru_label("marketing_price"), format_value(marketing_seller_price)),
        (ru_label("total_commission"), format_value(total_commission)),
        (ru_label("profit"), format_value(profit)),
        (ru_label("profit_margin"), f"{format_value(profit_margin)}%"),
    ]

    return Section(title="Расчёт прибыли", rows=rows)


def create_profit_for_min_section(item: Item, user_purchase_price: Decimal) -> Section:
    """Create profit calculation section."""
    minimal_price = item.price.min_price
    commission = item.fbs_commission_without_percent
    ozon_percent_value = (
        item.price.min_price * item.commissions.sales_percent_fbs / 100
    ).to_integral_value(ROUND_HALF_UP)

    total_commission = commission + ozon_percent_value
    profit = minimal_price - total_commission - user_purchase_price

    profit_margin = Decimal(0)
    if user_purchase_price > 0:
        profit_margin = (profit / user_purchase_price * 100).quantize(Decimal("0.01"))

    rows = [
        (ru_label("user_purchase_price"), format_value(user_purchase_price)),
        (ru_label("min_price"), format_value(minimal_price)),
        (ru_label("total_commission"), format_value(total_commission)),
        (ru_label("profit"), format_value(profit)),
        (ru_label("profit_margin"), f"{format_value(profit_margin)}%"),
    ]

    return Section(title="Расчёт прибыли от минимальной цены", rows=rows)


def sections_from_item(
    item: Item, user_purchase_price: Optional[Decimal] = None
) -> List[Section]:
    """Create sections from full Item model."""
    sections = []

    # Add profit section first if user provided purchase price
    if user_purchase_price is not None:
        profit_section = create_profit_section(item, user_purchase_price)
        profit_section_for_min_price = create_profit_for_min_section(
            item, user_purchase_price
        )
        sections.append(profit_section)
        sections.append(profit_section_for_min_price)

    # Main item section (exclude nested objects)
    main_section = create_section_from_model(
        item,
        "Основные поля",
        exclude_fields={"commissions", "marketing_actions", "price", "price_indexes"},
    )
    sections.append(main_section)

    # Commissions section
    commissions_section = create_section_from_model(item.commissions, "Комиссии")
    sections.append(commissions_section)

    # Price section
    price_section = create_section_from_model(item.price, "Цена")
    sections.append(price_section)

    # Price indexes sections
    price_index_sections = create_price_indexes_section(item.price_indexes)
    sections.extend(price_index_sections)

    # Marketing actions section
    marketing_section = create_marketing_actions_section(item.marketing_actions)
    sections.append(marketing_section)

    return sections
