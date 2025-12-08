# Plant Delivery API - Mobile App Integration Guide

## Base Configuration

**Production Base URL:** `http://3.111.165.191/api/v1`

**API Documentation:** `http://3.111.165.191/docs`

**Health Check:** `http://3.111.165.191/health`

---

## Authentication

The API uses **Bearer Token Authentication** (JWT). After login, include the token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Authentication Flow

1. **Register** → Get user details
2. **Login** → Get access token
3. **Use token** → Include in all authenticated requests

---

## API Endpoints

### 1. Authentication Endpoints

#### 1.1 Register User

**POST** `/api/v1/auth/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123",
  "phone": "+1234567890",
  "address": "123 Main St, City",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Available Roles:** `user`, `seller`, `admin`, `super_admin`, `manager`

---

#### 1.2 Login

**POST** `/api/v1/auth/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the `access_token` for authenticated requests!**

---

#### 1.3 Get Current User

**GET** `/api/v1/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 2. User Profile Endpoints

#### 2.1 Update Profile

**PUT** `/api/v1/users/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "John Updated",
  "phone": "+1234567891",
  "address": "456 New St, City"
}
```

**Response (200 OK):** Same as Get Current User

---

### 3. Plants Endpoints

#### 3.1 List Plants

**GET** `/api/v1/plants/`

**Query Parameters:**
- `name` (optional): Filter by plant name
- `category` (optional): Filter by category
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `verified_only` (optional): Only show AI-verified plants (true/false)
- `page` (default: 1): Page number
- `size` (default: 20): Items per page

**Example:**
```
GET /api/v1/plants/?category=indoor&min_price=10&max_price=100&page=1&size=20
```

**Response (200 OK):**
```json
{
  "plants": [
    {
      "id": 1,
      "name": "Monstera Deliciosa",
      "description": "Beautiful indoor plant",
      "price": 29.99,
      "category": "indoor",
      "species": "Monstera",
      "care_instructions": "Water weekly, indirect sunlight",
      "stock_quantity": 15,
      "image_url": "https://example.com/plant1.jpg",
      "seller_id": 2,
      "verified_by_ai": true,
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

---

#### 3.2 Get Plant by ID

**GET** `/api/v1/plants/{plant_id}`

**Response (200 OK):** Single plant object (same structure as in list)

---

#### 3.3 Predict Plant from Image (AI)

**POST** `/api/v1/plants/predict`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `image`: Image file (JPEG, PNG)

**Response (200 OK):**
```json
{
  "is_plant": true,
  "plant_type": "Monstera Deliciosa",
  "confidence": 0.95,
  "prediction_id": 123
}
```

---

#### 3.4 Get Prediction History

**GET** `/api/v1/plants/predictions/history`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (default: 50): Number of predictions to return

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "image_url": "https://example.com/prediction1.jpg",
    "is_plant": true,
    "plant_type": "Monstera Deliciosa",
    "confidence": 0.95,
    "uploaded_by": 1,
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

---

### 4. Cart Endpoints

#### 4.1 Get Cart

**GET** `/api/v1/cart/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
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

---

#### 4.2 Add Item to Cart

**POST** `/api/v1/cart/items`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "plant_id": 5,
  "quantity": 2
}
```

**Response (200 OK):** Updated cart object

---

#### 4.3 Update Cart Item

**PUT** `/api/v1/cart/items/{item_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "quantity": 3
}
```

**Response (200 OK):** Updated cart object

---

#### 4.4 Remove Item from Cart

**DELETE** `/api/v1/cart/items/{item_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):** Updated cart object

---

#### 4.5 Clear Cart

**DELETE** `/api/v1/cart/clear`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):** Empty cart object

---

### 5. Orders Endpoints

#### 5.1 Checkout (Create Orders from Cart)

**POST** `/api/v1/orders/checkout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "shipping_address": "123 Main St, City, State, ZIP",
  "notes": "Please deliver in the morning",
  "payment_method": "cod"
}
```

**Payment Methods:** `cod` (Cash on Delivery) or `razorpay`

**Response (200 OK):**
```json
{
  "orders": [
    {
      "order_id": 10,
      "seller_id": 2,
      "total_price": 59.98,
      "status": "pending"
    }
  ],
  "payment_required": false,
  "payment_provider": null,
  "payment_payload": null
}
```

**For Razorpay:**
```json
{
  "orders": [...],
  "payment_required": true,
  "payment_provider": "razorpay",
  "payment_payload": {}
}
```

---

#### 5.2 Get My Orders

**GET** `/api/v1/orders/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (default: 1)
- `size` (default: 20)

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": 10,
      "buyer_id": 1,
      "seller_id": 2,
      "delivery_agent_id": null,
      "status": "pending",
      "total_price": 59.98,
      "shipping_address": "123 Main St, City",
      "notes": "Please deliver in the morning",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": null,
      "order_items": [
        {
          "id": 1,
          "plant_id": 5,
          "quantity": 2,
          "unit_price": 29.99,
          "plant_name": "Monstera Deliciosa"
        }
      ]
    }
  ],
  "total": 5,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

**Order Statuses:** `pending`, `confirmed`, `shipped`, `delivered`, `cancelled`

---

#### 5.3 Get Order by ID

**GET** `/api/v1/orders/{order_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):** Single order object

---

#### 5.4 Get Order Timeline

**GET** `/api/v1/orders/{order_id}/timeline`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "timeline": [
    {
      "status": "pending",
      "note": "Order placed",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "status": "confirmed",
      "note": "Order confirmed by seller",
      "timestamp": "2024-01-15T11:00:00Z"
    }
  ]
}
```

---

#### 5.5 Cancel Order

**PUT** `/api/v1/orders/{order_id}/cancel`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Order cancelled successfully"
}
```

---

#### 5.6 Get Order Statistics

**GET** `/api/v1/orders/stats/my-stats`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total_orders": 10,
  "pending_orders": 2,
  "completed_orders": 7,
  "cancelled_orders": 1,
  "total_revenue": 599.80
}
```

---

### 6. Payments Endpoints

#### 6.1 Create Razorpay Order

**POST** `/api/v1/payments/razorpay/order`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "order_id": 10
}
```

**Response (200 OK):**
```json
{
  "provider": "razorpay",
  "amount": 59.98,
  "currency": "INR",
  "provider_order_id": "order_abc123",
  "receipt": "order_10"
}
```

**Use this data to initialize Razorpay payment in your mobile app.**

---

#### 6.2 Confirm COD Payment

**POST** `/api/v1/payments/cod/confirm`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "order_id": 10
}
```

**Response (200 OK):**
```json
{
  "message": "COD confirmed",
  "order_id": 10
}
```

---

### 7. Reviews Endpoints

#### 7.1 Create Review

**POST** `/api/v1/reviews/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "plant_id": 5,
  "rating": 5,
  "comment": "Great plant, very healthy!"
}
```

**Rating:** 1-5 (integer)

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "plant_id": 5,
  "rating": 5,
  "comment": "Great plant, very healthy!",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### 7.2 Get Reviews for Plant

**GET** `/api/v1/reviews/?plant_id={plant_id}`

**Response (200 OK):**
```json
{
  "reviews": [
    {
      "id": 1,
      "user_id": 1,
      "plant_id": 5,
      "rating": 5,
      "comment": "Great plant!",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "average_rating": 4.5,
  "total": 10
}
```

---

### 8. Categories Endpoints

#### 8.1 Get Categories

**GET** `/api/v1/categories/`

**Response (200 OK):**
```json
{
  "categories": [
    {
      "id": "indoor",
      "name": "Indoor Plants",
      "subcategories": ["succulents", "ferns", "tropical"]
    },
    {
      "id": "outdoor",
      "name": "Outdoor Plants",
      "subcategories": ["trees", "shrubs", "flowers"]
    }
  ]
}
```

---

### 9. Health Check

**GET** `/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini": "connected",
  "environment": "production"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "path": "/api/v1/endpoint"
}
```

### Common HTTP Status Codes

- **200 OK**: Success
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Example Error Response

```json
{
  "error": "Validation error",
  "message": "Email is required",
  "path": "/api/v1/auth/register"
}
```

---

## Mobile App Integration Examples

### Android (Kotlin + Retrofit)

#### 1. API Service Interface

```kotlin
interface PlantDeliveryAPI {
    @POST("auth/register")
    suspend fun register(@Body user: UserCreate): Response<UserResponse>
    
    @POST("auth/login")
    suspend fun login(@Body credentials: UserLogin): Response<TokenResponse>
    
    @GET("auth/me")
    suspend fun getCurrentUser(@Header("Authorization") token: String): Response<UserResponse>
    
    @GET("plants/")
    suspend fun getPlants(
        @Query("page") page: Int = 1,
        @Query("size") size: Int = 20,
        @Query("category") category: String? = null
    ): Response<PlantListResponse>
    
    @Multipart
    @POST("plants/predict")
    suspend fun predictPlant(
        @Header("Authorization") token: String,
        @Part image: MultipartBody.Part
    ): Response<PredictionResponse>
    
    @GET("cart/")
    suspend fun getCart(@Header("Authorization") token: String): Response<CartResponse>
    
    @POST("cart/items")
    suspend fun addToCart(
        @Header("Authorization") token: String,
        @Body item: CartItemCreate
    ): Response<CartResponse>
    
    @POST("orders/checkout")
    suspend fun checkout(
        @Header("Authorization") token: String,
        @Body request: CheckoutRequest
    ): Response<CheckoutResponse>
}

// Data Classes
data class UserCreate(
    val name: String,
    val email: String,
    val password: String,
    val phone: String? = null,
    val address: String? = null,
    val role: String = "user"
)

data class UserLogin(
    val email: String,
    val password: String
)

data class TokenResponse(
    val access_token: String,
    val token_type: String
)

data class PlantResponse(
    val id: Int,
    val name: String,
    val description: String?,
    val price: Double,
    val category: String?,
    val image_url: String?,
    val stock_quantity: Int,
    val verified_by_ai: Boolean
)

data class PlantListResponse(
    val plants: List<PlantResponse>,
    val total: Int,
    val page: Int,
    val size: Int,
    val pages: Int
)

data class CartItemCreate(
    val plant_id: Int,
    val quantity: Int
)

data class CartResponse(
    val id: Int,
    val items: List<CartItem>,
    val total_quantity: Int,
    val total_price: Double
)

data class CheckoutRequest(
    val shipping_address: String,
    val notes: String? = null,
    val payment_method: String
)
```

#### 2. Retrofit Setup

```kotlin
object ApiClient {
    private const val BASE_URL = "http://3.111.165.191/api/v1/"
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor { chain ->
            val request = chain.request()
            val response = chain.proceed(request)
            response
        }
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val api: PlantDeliveryAPI = retrofit.create(PlantDeliveryAPI::class.java)
}

// Usage
class MainActivity : AppCompatActivity() {
    private val api = ApiClient.api
    
    suspend fun login(email: String, password: String) {
        try {
            val response = api.login(UserLogin(email, password))
            if (response.isSuccessful) {
                val token = response.body()?.access_token
                // Save token to SharedPreferences
                saveToken(token)
            }
        } catch (e: Exception) {
            // Handle error
        }
    }
    
    suspend fun getPlants() {
        val response = api.getPlants(page = 1, size = 20)
        if (response.isSuccessful) {
            val plants = response.body()?.plants
            // Update UI
        }
    }
    
    suspend fun predictPlant(imageFile: File) {
        val token = getToken() // Get saved token
        val requestFile = imageFile.asRequestBody("image/*".toMediaType())
        val imagePart = MultipartBody.Part.createFormData("image", imageFile.name, requestFile)
        
        val response = api.predictPlant("Bearer $token", imagePart)
        if (response.isSuccessful) {
            val prediction = response.body()
            // Show prediction result
        }
    }
}
```

---

### iOS (Swift + URLSession)

```swift
import Foundation

class PlantDeliveryAPI {
    static let baseURL = "http://3.111.165.191/api/v1"
    
    // MARK: - Authentication
    static func register(user: UserCreate, completion: @escaping (Result<UserResponse, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/auth/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONEncoder().encode(user)
        } catch {
            completion(.failure(error))
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else { return }
            
            do {
                let userResponse = try JSONDecoder().decode(UserResponse.self, from: data)
                completion(.success(userResponse))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    static func login(email: String, password: String, completion: @escaping (Result<TokenResponse, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let credentials = UserLogin(email: email, password: password)
        request.httpBody = try? JSONEncoder().encode(credentials)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else { return }
            
            do {
                let tokenResponse = try JSONDecoder().decode(TokenResponse.self, from: data)
                // Save token to UserDefaults
                UserDefaults.standard.set(tokenResponse.access_token, forKey: "access_token")
                completion(.success(tokenResponse))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    // MARK: - Plants
    static func getPlants(page: Int = 1, size: Int = 20, completion: @escaping (Result<PlantListResponse, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/plants/?page=\(page)&size=\(size)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else { return }
            
            do {
                let plants = try JSONDecoder().decode(PlantListResponse.self, from: data)
                completion(.success(plants))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    // MARK: - Cart
    static func getCart(completion: @escaping (Result<CartResponse, Error>) -> Void) {
        guard let token = UserDefaults.standard.string(forKey: "access_token") else {
            completion(.failure(NSError(domain: "Auth", code: 401)))
            return
        }
        
        let url = URL(string: "\(baseURL)/cart/")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else { return }
            
            do {
                let cart = try JSONDecoder().decode(CartResponse.self, from: data)
                completion(.success(cart))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

// MARK: - Data Models
struct UserCreate: Codable {
    let name: String
    let email: String
    let password: String
    let phone: String?
    let address: String?
    let role: String
}

struct UserLogin: Codable {
    let email: String
    let password: String
}

struct TokenResponse: Codable {
    let access_token: String
    let token_type: String
}

struct PlantResponse: Codable {
    let id: Int
    let name: String
    let description: String?
    let price: Double
    let category: String?
    let image_url: String?
    let stock_quantity: Int
    let verified_by_ai: Bool
}

struct PlantListResponse: Codable {
    let plants: [PlantResponse]
    let total: Int
    let page: Int
    let size: Int
    let pages: Int
}
```

---

### React Native (JavaScript/TypeScript)

```typescript
// api.ts
const BASE_URL = 'http://3.111.165.191/api/v1';

class PlantDeliveryAPI {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Request failed');
    }

    return response.json();
  }

  // Authentication
  async register(userData: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    address?: string;
    role?: string;
  }) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(email: string, password: string) {
    const response = await this.request<{
      access_token: string;
      token_type: string;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    this.setToken(response.access_token);
    // Save to AsyncStorage
    await AsyncStorage.setItem('access_token', response.access_token);
    
    return response;
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  // Plants
  async getPlants(params?: {
    page?: number;
    size?: number;
    category?: string;
    min_price?: number;
    max_price?: number;
  }) {
    const queryString = new URLSearchParams(
      params as any
    ).toString();
    return this.request(`/plants/?${queryString}`);
  }

  async predictPlant(imageUri: string) {
    const formData = new FormData();
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'plant.jpg',
    } as any);

    const response = await fetch(`${BASE_URL}/plants/predict`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Prediction failed');
    }

    return response.json();
  }

  // Cart
  async getCart() {
    return this.request('/cart/');
  }

  async addToCart(plantId: number, quantity: number) {
    return this.request('/cart/items', {
      method: 'POST',
      body: JSON.stringify({ plant_id: plantId, quantity }),
    });
  }

  // Orders
  async checkout(shippingAddress: string, paymentMethod: string) {
    return this.request('/orders/checkout', {
      method: 'POST',
      body: JSON.stringify({
        shipping_address: shippingAddress,
        payment_method: paymentMethod,
      }),
    });
  }

  async getOrders(page: number = 1, size: number = 20) {
    return this.request(`/orders/?page=${page}&size=${size}`);
  }
}

export const api = new PlantDeliveryAPI();

// Usage in component
import { api } from './api';

const LoginScreen = () => {
  const handleLogin = async () => {
    try {
      await api.login('user@example.com', 'password');
      // Navigate to home
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
};
```

---

### Flutter (Dart)

```dart
// api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class PlantDeliveryAPI {
  static const String baseURL = 'http://3.111.165.191/api/v1';
  String? _token;

  Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
  }

  Future<String?> getToken() async {
    if (_token != null) return _token;
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Map<String, String> _getHeaders({bool includeAuth = false}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    
    if (includeAuth && _token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    
    return headers;
  }

  // Authentication
  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String password,
    String? phone,
    String? address,
  }) async {
    final response = await http.post(
      Uri.parse('$baseURL/auth/register'),
      headers: _getHeaders(),
      body: jsonEncode({
        'name': name,
        'email': email,
        'password': password,
        'phone': phone,
        'address': address,
        'role': 'user',
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Registration failed');
    }
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseURL/auth/login'),
      headers: _getHeaders(),
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await setToken(data['access_token']);
      return data;
    } else {
      throw Exception('Login failed');
    }
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    await getToken(); // Load token from storage
    final response = await http.get(
      Uri.parse('$baseURL/auth/me'),
      headers: _getHeaders(includeAuth: true),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get user');
    }
  }

  // Plants
  Future<Map<String, dynamic>> getPlants({
    int page = 1,
    int size = 20,
    String? category,
  }) async {
    final queryParams = <String, String>{
      'page': page.toString(),
      'size': size.toString(),
    };
    if (category != null) queryParams['category'] = category;

    final uri = Uri.parse('$baseURL/plants/').replace(queryParameters: queryParams);
    final response = await http.get(uri, headers: _getHeaders());

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get plants');
    }
  }

  // Cart
  Future<Map<String, dynamic>> getCart() async {
    await getToken();
    final response = await http.get(
      Uri.parse('$baseURL/cart/'),
      headers: _getHeaders(includeAuth: true),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get cart');
    }
  }

  Future<Map<String, dynamic>> addToCart(int plantId, int quantity) async {
    await getToken();
    final response = await http.post(
      Uri.parse('$baseURL/cart/items'),
      headers: _getHeaders(includeAuth: true),
      body: jsonEncode({
        'plant_id': plantId,
        'quantity': quantity,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to add to cart');
    }
  }

  // Orders
  Future<Map<String, dynamic>> checkout({
    required String shippingAddress,
    required String paymentMethod,
    String? notes,
  }) async {
    await getToken();
    final response = await http.post(
      Uri.parse('$baseURL/orders/checkout'),
      headers: _getHeaders(includeAuth: true),
      body: jsonEncode({
        'shipping_address': shippingAddress,
        'payment_method': paymentMethod,
        'notes': notes,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Checkout failed');
    }
  }
}

// Usage
final api = PlantDeliveryAPI();

// Login
await api.login('user@example.com', 'password');

// Get plants
final plants = await api.getPlants(page: 1, size: 20);

// Add to cart
await api.addToCart(plantId: 5, quantity: 2);

// Checkout
await api.checkout(
  shippingAddress: '123 Main St',
  paymentMethod: 'cod',
);
```

---

## Complete JSON Schemas

See `api-schemas.json` for complete JSON Schema definitions for all data models.

---

## Best Practices

1. **Token Storage**: Store access tokens securely (Keychain on iOS, Keystore on Android, SecureStorage in React Native/Flutter)

2. **Error Handling**: Always handle network errors and API errors gracefully

3. **Loading States**: Show loading indicators during API calls

4. **Retry Logic**: Implement retry logic for failed requests (especially for network errors)

5. **Token Refresh**: Implement token refresh if your app supports long sessions

6. **Image Upload**: Compress images before uploading to reduce payload size

7. **Pagination**: Implement infinite scroll or pagination for list endpoints

8. **Caching**: Cache frequently accessed data (plants, categories) to reduce API calls

---

## Support

For API documentation and testing, visit: `http://3.111.165.191/docs`

For issues or questions, check the API health endpoint: `http://3.111.165.191/health`

