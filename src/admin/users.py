from sqladmin import ModelView

from src.admin.utils import get_sqladmin_mixin
from src.settings.constants import NUMBER_OF_DOTS_AFTER_REDUCTION, PASSWORD_LENTH_ADMIN, AdminIcons
from src.users.models import User


class UserAdmin(get_sqladmin_mixin(User), ModelView, model=User):
    """
    Admin view for User model.

    Search fields: id, email, username
    Sortable fields: id, email, username, updated_at
    Password is limited to 8 symbols for security reasons.
    """

    column_list = [
        User.id,
        User.email,
        User.username,
        User.password,
        User.updated_at,
        User.deleted_at,
    ]
    column_searchable_list = [User.id, User.email, User.username]
    column_sortable_list = [User.id, User.email, User.username, User.updated_at]
    column_formatters = {
        User.password: lambda m,
        _: f"{m.password[:PASSWORD_LENTH_ADMIN]}{'.' * NUMBER_OF_DOTS_AFTER_REDUCTION}"
    }
    column_labels = {User.password: "hashed password"}
    column_details_excluide_list = [User.password]

    name = "User"
    name_plural = "Users"
    icon = AdminIcons.USERS_ICON
