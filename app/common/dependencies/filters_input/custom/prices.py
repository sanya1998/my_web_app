from pydantic import BaseModel, computed_field


class PricesFiltersInput(BaseModel):
    price_min: int | None = None
    price_max: int | None = None

    @computed_field
    @property
    def prices(self) -> tuple[int | None, int | None] | None:
        return (self.price_min, self.price_max) if self.price_min or self.price_max else None
