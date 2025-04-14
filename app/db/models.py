from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Integer,
    ForeignKey, Table, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

Base = declarative_base()

restaurant_cuisine = Table(
    "restaurant_cuisine",
    Base.metadata,
    Column("restaurant_id", UUID(as_uuid=True), ForeignKey("restaurants.id"), primary_key=True),
    Column("cuisine_id", UUID(as_uuid=True), ForeignKey("cuisines.id"), primary_key=True)
)

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    small_description = Column(String)
    large_description = Column(Text)
    attributes = Column(JSON)
    location_hash = Column(String)  # Simplified placeholder for now
    avg_rating = Column(Float, default=0.0)
    num_reviews = Column(Integer, default=0)
    price_range = Column(Integer)  # e.g. 1 = cheap, 2 = medium, 3 = expensive
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    cuisines = relationship("Cuisine", secondary=restaurant_cuisine, back_populates="restaurants")
    dishes = relationship("Dish", back_populates="restaurant")


class Cuisine(Base):
    __tablename__ = "cuisines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    restaurants = relationship("Restaurant", secondary=restaurant_cuisine, back_populates="cuisines")


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    cuisine_id = Column(UUID(as_uuid=True), ForeignKey("cuisines.id"))
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"))
    price = Column(Integer)
    image_url = Column(String)
    is_featured = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="dishes")
    cuisine = relationship("Cuisine")

