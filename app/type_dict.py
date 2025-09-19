from typing import TypedDict

class PaymentItem(TypedDict):
    item_code: str
    product_type: str
    item_price: int
    item_name: str
    tax: int
    token_confirmation: str

class PackageToBuy(TypedDict):
    family_code: str
    is_enterprise: bool
    variant_name: str
    order: int