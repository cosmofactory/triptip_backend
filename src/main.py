import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from sqlalchemy import text

from src.admin.auth import authentication_backend
from src.admin.locations import LocationAdmin
from src.admin.trips import TripAdmin
from src.admin.users import UserAdmin
from src.auth.router import router as auth_router
from src.database.database import SessionDep, engine
from src.settings.config import settings
from src.trips.router import router as trips_router
from src.users.router import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(trips_router)


if sentry_key := settings.SENTRY_KEY:
    sentry_sdk.init(
        dsn=sentry_key,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        enable_tracing=True,
    )

origins = ["*"]


@app.get("/about_project")
async def read_root(db: SessionDep):
    """Just a simple test endpoint showing that the project somehow for no reason works."""
    try:
        result = await db.execute(text("SELECT 'Database works, yay!'"))
    except Exception as e:
        return {"Error": f"An error occurred during database query: {str(e)}"}
    return {
        "Info": "This is our project TripTip."
        " Here you will find the most amazing trips and plan your next adventure!"
        f" Database response: {result.all()[0][0]}"
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# SQLAdmin config
admin = Admin(
    app, engine=engine, title="TripTip Admin", authentication_backend=authentication_backend
)

admin.add_view(UserAdmin)
admin.add_view(TripAdmin)
admin.add_view(LocationAdmin)
