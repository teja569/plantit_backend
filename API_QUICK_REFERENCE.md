# Plant Delivery API - Quick Reference

## Base URL
```
http://3.111.165.191/api/v1
```

## Authentication
Include token in header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints Summary

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | Login user |
| GET | `/auth/me` | Yes | Get current user |

### User Profile
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| PUT | `/users/me` | Yes | Update profile |

### Plants
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/plants/` | No | List plants (with filters) |
| GET | `/plants/{id}` | No | Get plant by ID |
| POST | `/plants/predict` | Yes | Predict plant from image |
| GET | `/plants/predictions/history` | Yes | Get prediction history |

### Cart
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/cart/` | Yes | Get cart |
| POST | `/cart/items` | Yes | Add item to cart |
| PUT | `/cart/items/{id}` | Yes | Update cart item |
| DELETE | `/cart/items/{id}` | Yes | Remove item |
| DELETE | `/cart/clear` | Yes | Clear cart |

### Orders
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/orders/checkout` | Yes | Checkout cart |
| GET | `/orders/` | Yes | Get my orders |
| GET | `/orders/{id}` | Yes | Get order by ID |
| GET | `/orders/{id}/timeline` | Yes | Get order timeline |
| PUT | `/orders/{id}/cancel` | Yes | Cancel order |
| GET | `/orders/stats/my-stats` | Yes | Get order statistics |

### Payments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/payments/razorpay/order` | Yes | Create Razorpay order |
| POST | `/payments/cod/confirm` | Yes | Confirm COD payment |

### Reviews
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/reviews/` | Yes | Create review |
| GET | `/reviews/?plant_id={id}` | No | Get plant reviews |

### Stores
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/stores/nearby` | No (token optional) | Get nearby stores by lat/lng |

### Categories
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/categories/` | No | Get categories |

---

## Request/Response Examples

### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "user"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}

Response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### Get Plants
```http
GET /api/v1/plants/?page=1&size=20&category=indoor

Response:
{
  "plants": [...],
  "total": 50,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

### Add to Cart
```http
POST /api/v1/cart/items
Authorization: Bearer <token>
Content-Type: application/json

{
  "plant_id": 5,
  "quantity": 2
}
```

### Checkout
```http
POST /api/v1/orders/checkout
Authorization: Bearer <token>
Content-Type: application/json

{
  "shipping_address": "123 Main St",
  "payment_method": "cod"
}
```

---

## Data Models

### User
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Plant
```json
{
  "id": 1,
  "name": "Monstera Deliciosa",
  "description": "Beautiful indoor plant",
  "price": 29.99,
  "category": "indoor",
  "species": "Monstera",
  "care_instructions": "Water weekly",
  "stock_quantity": 15,
  "image_url": "https://example.com/plant.jpg",
  "seller_id": 2,
  "verified_by_ai": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Cart
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "plant_id": 5,
      "quantity": 2,
      "unit_price": 29.99
    }
  ],
  "total_quantity": 2,
  "total_price": 59.98
}
```

### Order
```json
{
  "id": 10,
  "buyer_id": 1,
  "seller_id": 2,
  "status": "pending",
  "total_price": 59.98,
  "shipping_address": "123 Main St",
  "order_items": [
    {
      "id": 1,
      "plant_id": 5,
      "quantity": 2,
      "unit_price": 29.99,
      "plant_name": "Monstera"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Prediction
```json
{
  "is_plant": true,
  "plant_type": "Monstera Deliciosa",
  "confidence": 0.95,
  "prediction_id": 123
}
```

### Store
```json
{
  "id": 1,
  "name": "Green Leaf Nursery",
  "address": "Road no. 1, Banjara Hills",
  "latitude": 17.435,
  "longitude": 78.394,
  "phone": "+91-9876543210",
  "rating": 4.6,
  "total_reviews": 23,
  "is_partner": true,
  "created_at": "2024-01-15T10:30:00Z",
  "distance_km": 1.2
}
```

---

## Order Statuses
- `pending` - Order placed, awaiting confirmation
- `confirmed` - Order confirmed by seller
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled

## Payment Methods
- `cod` - Cash on Delivery
- `razorpay` - Razorpay online payment

## User Roles
- `user` - Regular customer
- `seller` - Plant seller
- `admin` - Administrator
- `super_admin` - Super administrator
- `manager` - Manager

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

---

## Testing

**Interactive API Docs:** http://3.111.165.191/docs

**Health Check:** http://3.111.165.191/health

