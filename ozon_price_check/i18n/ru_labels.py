"""Russian labels for product data fields."""

RU_LABELS = {
    # Root Item
    "offer_id": "Артикул",
    "product_id": "ID товара",
    "volume_weight": "Объёмный вес",
    "acquiring": "Эквайринг",
    
    # Price
    "currency_code": "Валюта",
    "price": "Цена",
    "old_price": "Старая цена",
    "retail_price": "Розничная цена",
    "marketing_price": "Маркетинговая цена",
    "marketing_seller_price": "Маркетинговая цена продавца",
    "min_price": "Минимальная цена",
    "net_price": "Цена нетто",
    "vat": "НДС",
    "auto_action_enabled": "Автоакция включена",
    "auto_add_to_ozon_actions_list_enabled": "Автодобавление в акции Ozon",
    "min_price_for_auto_actions_enabled": "Минимальная цена для автоакций",
    "price_strategy_enabled": "Ценовая стратегия включена",
    
    # Commissions
    "sales_percent_fbo": "Процент продаж FBO",
    "sales_percent_fbs": "Процент продаж FBS",
    "fbo_deliv_to_customer_amount": "FBO: доставка покупателю",
    "fbo_direct_flow_trans_max_amount": "FBO: директ флоу (макс.)",
    "fbo_direct_flow_trans_min_amount": "FBO: директ флоу (мин.)",
    "fbo_return_flow_amount": "FBO: возврат",
    "fbs_deliv_to_customer_amount": "FBS: доставка покупателю",
    "fbs_direct_flow_trans_max_amount": "FBS: директ флоу (макс.)",
    "fbs_direct_flow_trans_min_amount": "FBS: директ флоу (мин.)",
    "fbs_first_mile_max_amount": "FBS: первая миля (макс.)",
    "fbs_first_mile_min_amount": "FBS: первая миля (мин.)",
    "fbs_return_flow_amount": "FBS: возврат",
    
    # PriceIndexes
    "color_index": "Цвет индекса",
    "price_index_value": "Значение индекса",
    "min_price_currency": "Валюта мин. цены",
    "external_index_data": "Внешние данные индекса",
    "ozon_index_data": "Данные индекса Ozon",
    "self_marketplaces_index_data": "Данные индекса собственных маркетплейсов",
    
    # MarketingActions
    "title": "Название акции",
    "value": "Величина",
    "date_from": "Дата начала",
    "date_to": "Дата окончания",
    "ozon_actions_exist": "Есть акции Ozon",
    "current_period_from": "Текущий период с",
    "current_period_to": "Текущий период по",
    "actions": "Акции",
    
    # Computed fields
    "fbs_commission_without_percent": "FBS комиссия без процента",
    "fbo_commission_without_percent": "FBO комиссия без процента",
    "fbs_ozon_percent": "FBS процент Ozon",
    "fbo_ozon_percent": "FBO процент Ozon",
    "fbs_total_commission": "FBS общая комиссия",
    "fbo_total_commission": "FBO общая комиссия",
    
    # Profit calculation fields
    "user_purchase_price": "Закупочная цена",
    "marketing_price": "Маркетинговая цена",
    "total_commission": "Общая комиссия",
    "profit": "Прибыль",
    "profit_margin": "Рентабельность",
}


def ru_label(key: str) -> str:
    """
    Return Russian label for field key.
    Falls back to formatted English if no mapping exists.
    """
    if key in RU_LABELS:
        return RU_LABELS[key]
    
    # Fallback: convert snake_case to readable format
    words = key.replace("_", " ").split()
    formatted_words = []
    
    for word in words:
        # Keep common abbreviations uppercase
        if word.lower() in ("fbo", "fbs", "api", "id", "vat", "url"):
            formatted_words.append(word.upper())
        else:
            formatted_words.append(word.capitalize())
    
    return " ".join(formatted_words)