import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.settings.config import settings
from sqlalchemy import text

from src.auth.router import router as auth_router
from src.database.database import async_session_maker
from src.users.router import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)


if sentry_key := settings.SENTRY_KEY:
    sentry_sdk.init(
        dsn=sentry_key,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        enable_tracing=True,
    )

origins = ["*"]


@app.get("/about_project")
async def read_root():
    """Just a simple test endpoint showing that the project somehow for no reason works."""

    async with async_session_maker() as session:
        try:
            result = await session.execute(text("SELECT 'Database works, yay!'"))
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
