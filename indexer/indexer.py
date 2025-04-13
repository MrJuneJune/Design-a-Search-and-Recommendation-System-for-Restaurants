from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from elasticsearch import Elasticsearch
from db.models import Restaurant 
import os
import time

DB_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb")
ES_URL = os.getenv("ES_URL", "http://elasticsearch:9200")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
es = Elasticsearch(ES_URL)

def index_all_restaurants():
    session = Session()
    print("🔁 Re-indexing all restaurants...")
    restaurants = session.query(Restaurant).all()

    for r in restaurants:
        doc = {
            "id": str(r.id),
            "name": r.name,
            "small_description": r.small_description,
            "large_description": r.large_description,
            "cuisines": [c.name for c in r.cuisines]
        }
        es.index(index="restaurants", id=doc["id"], body=doc)

    print(f"✅ Indexed {len(restaurants)} restaurants.")
    session.close()

if __name__ == "__main__":
    while True:
        index_all_restaurants()
        print("⏱ Sleeping 1 hour...")
        time.sleep(3600)

