from sqlalchemy import text

from src.database.database import async_session_maker
from fastapi import FastAPI

app = FastAPI()


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
