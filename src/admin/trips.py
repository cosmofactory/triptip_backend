from sqladmin import ModelView

from src.settings.constants import (
    DESCRIPTION_LENGTH_ADMIN,
    NUMBER_OF_DOTS_AFTER_REDUCTION,
    AdminIcons,
)
from src.trips.models import Trip


class TripAdmin(ModelView, model=Trip):
    """
    Admin view for Trip model.

    Search fields: id, name, description, author
    Sortable fields: id, name, author, updated_at
    Description is limited to 10 symbols.
    """

    column_list = [
        Trip.id,
        Trip.name,
        Trip.description,
        Trip.date_from,
        Trip.date_to,
        Trip.author,
        Trip.updated_at,
    ]
    column_searchable_list = [Trip.id, Trip.name, Trip.description, Trip.author]
    column_sortable_list = [Trip.id, Trip.name, Trip.author, Trip.updated_at]
    column_formatters = {
        Trip.description: lambda m,
        _: f"{m.description[:DESCRIPTION_LENGTH_ADMIN]}{'.' * NUMBER_OF_DOTS_AFTER_REDUCTION}"
    }
    column_details_exclude_list = [Trip.author_id]
    name = "Trip"
    name_plural = "Trips"
    icon = AdminIcons.TRIPS_ICON
