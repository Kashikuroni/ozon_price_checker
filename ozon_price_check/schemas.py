from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field

from ozon_price_check.utils import to_camel
from ozon_price_check.types import ZDateTime


class Commissions(BaseModel):
    fbo_deliv_to_customer_amount: Decimal
    fbo_direct_flow_trans_max_amount: Decimal
    fbo_direct_flow_trans_min_amount: Decimal
    fbo_return_flow_amount: Decimal
    fbs_deliv_to_customer_amount: Decimal
    fbs_direct_flow_trans_max_amount: Decimal
    fbs_direct_flow_trans_min_amount: Decimal
    fbs_first_mile_max_amount: Decimal
    fbs_first_mile_min_amount: Decimal
    fbs_return_flow_amount: Decimal
    sales_percent_fbo: Decimal
    sales_percent_fbs: Decimal


class MarketingAction(BaseModel):
    date_from: ZDateTime
    date_to: ZDateTime
    title: str
    value: float


class MarketingActions(BaseModel):
    actions: list[MarketingAction]
    current_period_from: Optional[ZDateTime]
    current_period_to: Optional[ZDateTime]
    ozon_actions_exist: bool


class Price(BaseModel):
    auto_action_enabled: bool
    auto_add_to_ozon_actions_list_enabled: bool
    currency_code: str
    marketing_price: Decimal
    marketing_seller_price: Decimal
    min_price: Decimal
    net_price: Decimal
    old_price: Decimal
    price: Decimal
    retail_price: Decimal
    vat: Decimal


class PriceIndexData(BaseModel):
    min_price: float
    min_price_currency: str
    price_index_value: float


class PriceIndexes(BaseModel):
    color_index: str
    external_index_data: Optional[PriceIndexData]
    ozon_index_data: Optional[PriceIndexData]
    self_marketplaces_index_data: Optional[PriceIndexData]


class Item(BaseModel):
    acquiring: Decimal
    commissions: Commissions
    marketing_actions: MarketingActions
    offer_id: str
    price: Price
    price_indexes: PriceIndexes
    product_id: int
    volume_weight: float

    @computed_field
    @property
    def fbs_commission_without_percent(self) -> Decimal:
        fields = [
            self.acquiring,
            # self.commissions.fbs_return_flow_amount,
            self.commissions.fbs_deliv_to_customer_amount,
            self.commissions.fbs_first_mile_max_amount,
            self.commissions.fbs_direct_flow_trans_max_amount,
        ]
        return sum(fields, Decimal(0))

    @computed_field
    @property
    def fbo_commission_without_percent(self) -> Decimal:
        fields = [
            self.acquiring,
            # self.commissions.fbo_return_flow_amount,
            self.commissions.fbo_deliv_to_customer_amount,
            self.commissions.fbo_direct_flow_trans_max_amount,
        ]
        return sum(fields, Decimal(0))

    @computed_field
    @property
    def fbs_ozon_percent(self) -> Decimal:
        return (
            self.price.marketing_seller_price * self.commissions.sales_percent_fbs / 100
        ).to_integral_value(ROUND_HALF_UP)

    @computed_field
    @property
    def fbo_ozon_percent(self) -> Decimal:
        return (
            self.price.marketing_seller_price * self.commissions.sales_percent_fbo / 100
        ).to_integral_value(ROUND_HALF_UP)

    @computed_field
    @property
    def fbs_total_commission(self) -> Decimal:
        return (
            self.fbs_ozon_percent + self.fbs_commission_without_percent
        ).to_integral_value(ROUND_HALF_UP)

    @computed_field
    @property
    def fbo_total_commission(self) -> Decimal:
        return (
            self.fbo_ozon_percent + self.fbo_commission_without_percent
        ).to_integral_value(ROUND_HALF_UP)


class ProductsResponse(BaseModel):
    cursor: str
    items: list[Item]
    total: int


class AutoActionStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class PriceItem(BaseModel):
    sku: str
    minimal_price: Decimal
    retail_price: Decimal
    before_descount_price: Decimal
    min_price_for_auto_actions_enabled: bool = True
    auto_action_enabled: Optional[AutoActionStatus] = AutoActionStatus.UNKNOWN
    auto_add_to_ozon_actions_list_enabled: Optional[AutoActionStatus] = (
        AutoActionStatus.UNKNOWN
    )
    price_strategy_enabled: Optional[AutoActionStatus] = AutoActionStatus.DISABLED

    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: str(v)},
        extra="ignore",
        populate_by_name=True,
        alias_generator=to_camel,
    )


class OzonPriceItem(BaseModel):
    auto_action_enabled: Optional[AutoActionStatus] = AutoActionStatus.UNKNOWN
    auto_add_to_ozon_actions_list_enabled: Optional[AutoActionStatus] = (
        AutoActionStatus.UNKNOWN
    )
    min_price: Decimal = Field(..., alias="minimal_price")
    min_price_for_auto_actions_enabled: bool = True
    offer_id: str = Field(..., alias="sku")
    old_price: Decimal = Field(..., alias="before_descount_price")
    price: Decimal = Field(..., alias="retail_price")
    price_strategy_enabled: Optional[AutoActionStatus] = AutoActionStatus.DISABLED

    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: str(v)},
        extra="ignore",
        populate_by_name=True,
    )


class PriceResponse(BaseModel):
    prices: list[OzonPriceItem]


class UpdatePriceReponseError(BaseModel):
    code: str
    message: str


class UpdatePriceReponse(BaseModel):
    product_id: int
    offer_id: str
    updated: bool
    errors: list[UpdatePriceReponseError]

    model_config = ConfigDict(
        extra="ignore", populate_by_name=True, alias_generator=to_camel
    )
