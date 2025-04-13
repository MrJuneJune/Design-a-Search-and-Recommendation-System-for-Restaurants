from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import DBFactory, Restaurant, Dish, Cuisine, init
from typing import List

# init()
app = APIRouter()

def get_db():
    SessionFactory = DBFactory.get_instance().get_session_factory()
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def healthcheck(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/v1/restaurants/search")
def get_restaurants(
    cuisines: List[str] = Query(..., description="Comma-separated list of cuisines"),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Restaurant)
          .join(Restaurant.cuisines)
          .filter(
              Cuisine.name.in_(cuisines)
          )
          .distinct(Restaurant.id)
    )
    return [{"id": str(r.id), "name": r.name} for r in query.distinct()]
