from sqladmin import ModelView

from src.admin.utils import get_sqladmin_mixin
from src.settings.constants import (
    DESCRIPTION_LENGTH_ADMIN,
    NUMBER_OF_DOTS_AFTER_REDUCTION,
    AdminIcons,
)
from src.trips.models import Route


class RouteAdmin(get_sqladmin_mixin(Route), ModelView, model=Route):
    """
    Admin view for Location model.

    Search fields: id, name, trip
    Sortable fields: id, name, trip, updated_at
    Description is limited to 10 symbols.
    """

    column_list = [
        Route.id,
        Route.name,
        Route.description,
        Route.updated_at,
    ]
    column_searchable_list = [Route.id, Route.name, Route.origin_id]
    column_sortable_list = [Route.id, Route.name, Route.origin_id, Route.updated_at]
    column_formatters = {
        Route.description: lambda m,
        _: f"{m.description[:DESCRIPTION_LENGTH_ADMIN]}{'.' * NUMBER_OF_DOTS_AFTER_REDUCTION}"
    }
    name = "Route"
    name_plural = "Routes"
    icon = AdminIcons.ROUTES_ICON
