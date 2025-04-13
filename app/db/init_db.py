from db.models import Base, Cuisine, Restaurant, Dish
from db.session import DBFactory
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import time

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
    if session.query(Cuisine).first():
        print("🟡 Mock data already exists, skipping...")
        return

    print("🌱 Inserting mock data...")

    # Create cuisines
    italian = Cuisine(name="italian", description="Pasta, pizza, olive oil")
    korean = Cuisine(name="korean", description="Kimchi, BBQ, rice")

    session.add_all([italian, korean])
    session.flush()  # get their IDs

    # Create restaurant
    r1 = Restaurant(
        name="Pasta Palace",
        small_description="Best pasta in town",
        large_description="Handmade pasta and imported cheese",
        attributes={"vegan": False, "outdoor_seating": True},
        location_hash="hash1",
        cuisines=[italian],
        avg_rating=4.5,
        num_reviews=132,
        price_range=2,
    )

    r2 = Restaurant(
        name="Seoul Kitchen",
        small_description="Authentic Korean Cuisine",
        large_description="Family recipes passed down for generations.",
        attributes={"vegan": True, "outdoor_seating": False},
        location_hash="hash2",
        cuisines=[korean],
        avg_rating=4.7,
        num_reviews=211,
        price_range=3,
    )

    session.add_all([r1, r2])
    session.flush()

    # Dishes
    d1 = Dish(
        name="Spaghetti Carbonara",
        description="Classic creamy pasta",
        cuisine=italian,
        restaurant=r1,
        price=1800,
    )

    d2 = Dish(
        name="Bibimbap",
        description="Rice bowl with veggies and egg",
        cuisine=korean,
        restaurant=r2,
        price=1600,
        is_featured=True
    )

    session.add_all([d1, d2])
    session.commit()
    print("✅ Mock data seeded.")

def init():
    factory = DBFactory.get_instance()
    engine = factory.get_engine()
    wait_for_db(engine)
    Base.metadata.create_all(engine)

    SessionFactory = factory.get_session_factory()
    session = SessionFactory()
    try:
        seed_mock_data(session)
    finally:
        session.close()

if __name__ == "__main__":
    init()

