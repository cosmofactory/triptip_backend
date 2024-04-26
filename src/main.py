from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.database.database import async_session_maker

app = FastAPI()

origins = [
    "https://api.triptip.pro/",
    "https://swagger.triptip.pro/",
    "https://triptip.pro/",
    "http://localhost",
    "http://localhost:8000",
]


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
