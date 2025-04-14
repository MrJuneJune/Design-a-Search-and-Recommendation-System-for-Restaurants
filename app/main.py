from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import DBFactory, Restaurant, Dish, Cuisine, init
from typing import List


from elasticsearch import Elasticsearch
import os

# Reset DB
init()

# Elastic search 
ES_URL = os.getenv("ES_URL", "http://elasticsearch:9200")
es = Elasticsearch(ES_URL)

def search_restaurants(query: str, lat: float = None, lon: float = None):
    """
    Search restaurants using full-text match across name, description, and cuisines.

    Scoring logic (Elasticsearch default BM25):
        _score = function of (
            term frequency in field,         # how often query term appears
            inverse document frequency,      # how rare the term is across all docs
            field length normalization,      # short fields weigh more
            optional field boost (name^3)    # custom boosts for relevance

    Field Boosts:
        name:                ^3    (very important)
        small_description:   ^2
        large_description:   ^1
        cuisines:            ^3    (strong influence)

    If lat/lon are provided, results are further boosted by proximity to user.
    """

    base_query = {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^3",
                        "small_description^2",
                        "large_description",
                        "cuisines^3"
                    ]
                }
            },
            "boost_mode": "multiply",
            "score_mode": "sum",
            "functions": []
        }
    }

    if lat is not None and lon is not None:
        # Add location boost using gaussian decay
        base_query["function_score"]["functions"].append({
            "gauss": {
                "location": {
                    "origin": {"lat": lat, "lon": lon},
                    "scale": "10km",
                    "offset": "1km",
                    "decay": 0.5
                }
            },
            "weight": 3.0  
        })

    result = es.search(index="restaurants", query=base_query)

    return [
        {
            "id": hit["_id"],
            "score": hit["_score"],
            **hit["_source"]
        }
        for hit in result["hits"]["hits"]
    ]


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


@app.get("/v3/restaurants/search")
def search(
    q: str = Query(...),
    lat: float = Query(None),
    lon: float = Query(None),
):
    results = search_restaurants(q, lat, lon)
    return results
