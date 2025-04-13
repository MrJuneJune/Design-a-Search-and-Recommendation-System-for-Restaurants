from db.models import Base, Cuisine, Restaurant, Dish
from db.session import DBFactory
from sqlalchemy.orm import Session
from datetime import datetime
from faker import Faker

import uuid
import time
import random

faker = Faker()

def wait_for_db(engine):
    while True:
        try:
            conn = engine.connect()
            conn.close()
            break
        except Exception:
            print("⏳ Waiting for DB...")
            time.sleep(1)


def seed_mock_data(session: Session):
    print("🌱 Seeding new mock data...")

    # Step 1: Create 10 cuisines
    cuisine_names = [
        "italian", "korean", "japanese", "chinese", "mexican",
        "thai", "indian", "french", "greek", "vietnamese"
    ]
    cuisines = [Cuisine(name=name, description=faker.sentence()) for name in cuisine_names]
    session.add_all(cuisines)
    session.flush()

    # Step 2: Create 100 restaurants
    restaurants = []
    for _ in range(100):
        assigned_cuisines = random.sample(cuisines, k=random.randint(1, 3))
        r = Restaurant(
            name=faker.company(),
            small_description=faker.catch_phrase(),
            large_description=faker.paragraph(),
            attributes={
                "vegan": faker.boolean(),
                "outdoor_seating": faker.boolean()
            },
            location_hash=f"hash_{faker.zipcode()}",
            cuisines=assigned_cuisines,
            avg_rating=round(random.uniform(2.5, 5.0), 1),
            num_reviews=random.randint(5, 1000),
            price_range=random.randint(1, 3),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        restaurants.append(r)
    session.add_all(restaurants)
    session.flush()

    # Step 3: Create dishes for each restaurant
    dishes = []
    for r in restaurants:
        for _ in range(random.randint(3, 10)):
            cuisine = random.choice(r.cuisines)
            d = Dish(
                name=faker.word().title() + " " + random.choice(["Special", "Delight", "Surprise"]),
                description=faker.sentence(),
                cuisine=cuisine,
                restaurant=r,
                price=random.randint(1000, 4000),
                image_url=faker.image_url(),
                is_featured=random.choice([True, False]),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            dishes.append(d)
    session.add_all(dishes)
    session.commit()

    print(f"✅ Seeded {len(cuisines)} cuisines, {len(restaurants)} restaurants, {len(dishes)} dishes.")


def init():
    factory = DBFactory.get_instance()
    engine = factory.get_engine()
    wait_for_db(engine)
    Base.metadata.create_all(engine)

    SessionFactory = factory.get_session_factory()
    session = SessionFactory()
    try:
        print("🔥 Dropping all tables...")
        Base.metadata.drop_all(engine)
        
        print("📦 Creating tables...")
        Base.metadata.create_all(engine)
        seed_mock_data(session)
    finally:
        session.close()

if __name__ == "__main__":
    init()

