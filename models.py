from typing import Self

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator


class Product(BaseModel):
    """Ombordagi bitta mahsulot."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    price: int = Field(gt=0)
    stock: int = Field(ge=0)


class ProductList(RootModel[list[Product]]):
    """products.json faylining ildiz modeli."""


class Sale(BaseModel):
    """Tarixga yozilgan bitta sotuv."""

    model_config = ConfigDict(str_strip_whitespace=True)

    product_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: int = Field(gt=0)
    total: int = Field(ge=0)
    time: str

    @model_validator(mode="after")
    def check_total(self) -> Self:
        if self.total != self.unit_price * self.quantity:
            raise ValueError(
                "total unit_price * quantity ga teng bo'lishi kerak"
            )
        return self


class SaleList(RootModel[list[Sale]]):
    """sales.json faylining ildiz modeli."""


class BestSeller(BaseModel):
    """Hisobot uchun eng ko'p sotilgan mahsulot."""

    name: str
    quantity: int
