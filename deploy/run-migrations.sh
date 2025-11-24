#!/bin/bash
cd /opt/plant-delivery-api
source venv/bin/activate

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Run migrations
alembic upgrade head

echo "Migrations completed!"

