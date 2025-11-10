@echo off
REM Plant Delivery API Startup Script for Windows

echo 🌿 Starting Plant Delivery API...

REM Create necessary directories
if not exist logs mkdir logs
if not exist models mkdir models

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Copying from env.example...
    copy env.example .env
    echo 📝 Please update .env file with your configuration
)

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Create placeholder ML model if it doesn't exist
if not exist models\plant_classifier.onnx (
    echo 🤖 Creating placeholder ML model...
    python create_placeholder_model.py
)

REM Run database migrations
echo 🗄️  Running database migrations...
alembic upgrade head

REM Start the application
echo 🚀 Starting FastAPI application...
python main.py

pause
