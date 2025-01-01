from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

class Movie(BaseModel):
    id: int
    title: str
    genre: str
    year: int

movies = [
    Movie(id=1, title="Inception", genre="Sci-Fi", year=2010),
    Movie(id=2, title="The Dark Knight", genre="Action", year=2008),
    Movie(id=3, title="Interstellar", genre="Sci-Fi", year=2014),
]

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_movies(request: Request):
    return templates.TemplateResponse("movies.html", {"request": request, "movies": movies})

@app.get("/api/movies", response_model=List[Movie])
async def get_movies():
    return movies