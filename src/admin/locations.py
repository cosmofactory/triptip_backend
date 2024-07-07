from sqladmin import ModelView

from src.admin.utils import get_sqladmin_mixin
from src.settings.constants import (
    DESCRIPTION_LENGTH_ADMIN,
    NUMBER_OF_DOTS_AFTER_REDUCTION,
    AdminIcons,
)
from src.trips.models import Location


class LocationAdmin(get_sqladmin_mixin(Location), ModelView, model=Location):
    """
    Admin view for Location model.

    Search fields: id, name, trip
    Sortable fields: id, name, trip, updated_at
    Description is limited to 10 symbols.
    """

    column_list = [
        Location.id,
        Location.name,
        Location.description,
        Location.trip,
        Location.updated_at,
    ]
    column_searchable_list = [Location.id, Location.name, Location.trip_id]
    column_sortable_list = [Location.id, Location.name, Location.trip_id, Location.updated_at]
    column_formatters = {
        Location.description: lambda m,
        _: f"{m.description[:DESCRIPTION_LENGTH_ADMIN]}{'.' * NUMBER_OF_DOTS_AFTER_REDUCTION}"
    }
    name = "Location"
    name_plural = "Locations"
    icon = AdminIcons.LOCATIONS_ICON
