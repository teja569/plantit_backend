#!/bin/bash
cd /opt/plant-delivery-api
source venv/bin/activate
export PYTHONPATH=/opt/plant-delivery-api

python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/opt/plant-delivery-api')

from app.core.database import Base, engine

print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")
except Exception as e:
    print(f"✗ Error creating tables: {e}")
    import traceback
    traceback.print_exc()
PYTHON_SCRIPT

