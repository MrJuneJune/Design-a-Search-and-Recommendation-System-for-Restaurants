from fastapi import FastAPI, APIRouter, Depends, Query
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import DBFactory, Restaurant, Dish, Cuisine, init
from typing import List


from elasticsearch import Elasticsearch
import os

# Reset DB
# init()

# Elastic search 
ES_URL = os.getenv("ES_URL", "http://elasticsearch:9200")
es = Elasticsearch(ES_URL)

def search_restaurants(query: str, lat: float = None, lon: float = None):
    """
    Search restaurants using full-text match across name, description, and cuisines.
    If query is empty, only return restaurants near (lat, lon) using geo filter.
    """

    if query.strip() == "" and lat is not None and lon is not None:
        # Location-only search (no full-text match)
        base_query = {
            "bool": {
                "filter": {
                    "geo_distance": {
                        "distance": "10km",
                        "location": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
            }
        }

    else:
        # Full-text search + optional location boosting
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

app = FastAPI()

# Allowing CORS since it is just for view.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
