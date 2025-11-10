# Plant Delivery API

A production-ready FastAPI backend for Plant Delivery Mobile App with AI-powered plant detection and classification.

## Features

🌿 **Core Functionality**
- User authentication with JWT and role-based access control
- Plant listing management with image upload
- AI-powered plant detection and classification
- Order management and tracking
- Delivery agent assignment and tracking
- Seller onboarding and dashboard
- Admin panel with analytics

🤖 **AI/ML Integration**
- Plant detection (is_plant / not_plant)
- Plant species classification
- Confidence scoring
- Prediction logging

📊 **Analytics & Reporting**
- Admin dashboard with comprehensive statistics
- Seller performance metrics
- Revenue tracking
- Order analytics
- User statistics

## Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Authentication**: JWT with role-based access control
- **ML**: ONNX Runtime for plant classification
- **Storage**: AWS S3 for image storage
- **Deployment**: Docker + Railway
- **Logging**: Structured logging with Loguru

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd plant-delivery-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

Update the following variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`: For S3 storage
- `ML_MODEL_PATH`: Path to your ONNX model file

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# Or create tables directly
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 4. Run the Application

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
python main.py
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Plants
- `GET /api/v1/plants/` - List plants with filtering
- `POST /api/v1/plants/` - Create plant listing
- `GET /api/v1/plants/{id}` - Get plant details
- `POST /api/v1/plants/predict` - AI plant prediction

### Orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/` - Get user orders
- `PUT /api/v1/orders/{id}/status` - Update order status

### Seller
- `POST /api/v1/seller/onboard` - Seller onboarding
- `GET /api/v1/seller/dashboard` - Seller dashboard
- `GET /api/v1/seller/earnings` - Earnings breakdown

### Admin
- `GET /api/v1/admin/dashboard` - Admin dashboard
- `GET /api/v1/admin/stats/*` - Various statistics
- `GET /api/v1/admin/health` - System health

### Delivery
- `GET /api/v1/delivery/agents` - List delivery agents
- `POST /api/v1/delivery/orders/{id}/assign` - Assign delivery agent

## ML Model Integration

The API includes a plant classification system that:

1. **Accepts image uploads** via `/api/v1/plants/predict`
2. **Detects if image contains a plant** (binary classification)
3. **Classifies plant species** (multi-class classification)
4. **Returns confidence scores** for predictions
5. **Logs all predictions** for analysis

### Model Requirements

- ONNX format model file
- Input: 224x224 RGB image
- Output: [is_plant_prob, plant_type_probs...]
- Place model file at path specified in `ML_MODEL_PATH`

## Database Schema

### Core Tables
- `users` - User accounts with role-based access
- `plants` - Plant listings with AI verification
- `orders` - Order management
- `order_items` - Order line items
- `predictions` - ML prediction logs
- `delivery_agents` - Delivery personnel

### Key Relationships
- Users can be buyers, sellers, or admins
- Plants belong to sellers
- Orders connect buyers, sellers, and delivery agents
- Predictions track ML model usage

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t plant-delivery-api .

# Run container
docker run -p 8000:8000 --env-file .env plant-delivery-api
```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Railway will auto-deploy on git push

### Environment Variables

Required for production:
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - JWT secret
- `AWS_ACCESS_KEY_ID` - S3 access key
- `AWS_SECRET_ACCESS_KEY` - S3 secret key
- `AWS_BUCKET_NAME` - S3 bucket name

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Development

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Security Features

- JWT-based authentication
- Role-based access control
- Rate limiting
- CORS protection
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

## Monitoring & Logging

- Structured logging with Loguru
- Request/response logging
- Error tracking
- Performance metrics
- Health check endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the logs for debugging information
