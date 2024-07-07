from sqladmin import ModelView

from src.database.database import Base


def get_sqladmin_mixin(model: Base) -> ModelView:
    class SQLAdminMixin(ModelView):
        form_excluded_columns = [model.created_at, model.updated_at, model.deleted_at]

    return SQLAdminMixin
