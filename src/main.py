from fastapi import FastAPI

app = FastAPI()


@app.get("/about_project")
async def read_root():
    """Just a simple test endpoint showing that the project somehow for no reason works."""
    return {
        "Info": "This is our project TripTip."
        "Here you will find the most amazing trips and plan your next adventure!"
    }
