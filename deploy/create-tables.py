#!/usr/bin/env python3
"""Create database tables"""
from app.core.database import Base, engine

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

