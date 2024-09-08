from app.common.filtersets.custom_filters.dates import DatesFilter
from sqlalchemy_filterset import BaseFilterSet


class DatesFiltersSet(BaseFilterSet):
    dates = DatesFilter()
