from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import DBFactory, Restaurant, Dish, Cuisine, init
from typing import List


from elasticsearch import Elasticsearch
import os

ES_URL = os.getenv("ES_URL", "http://elasticsearch:9200")
es = Elasticsearch(ES_URL)

def search_restaurants(query: str):
    """
    serach restauarant, and we do it by calculating socre
    _score = function of (
        term frequency in field,
        how rare the term is in the index,
        field length,
        optional field boost
    )    
    """
    result = es.search(index="restaurants", query={
        "multi_match": {
            "query": query,
            "fields": ["name", "small_description", "large_description", "cuisines"]
        }
    })

    return [
        {
            "id": hit["_id"],
            "score": hit["_score"],
            **hit["_source"]
        }
        for hit in result["hits"]["hits"]
    ]


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


@app.get("/v2/restaurants/search")
def search(q: str = Query(...)):
    results = search_restaurants(q)
    return results
