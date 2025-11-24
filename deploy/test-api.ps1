# Test API Endpoints
$baseUrl = "http://3.111.165.191"

Write-Host "=== Testing Plant Delivery API ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri ($baseUrl + "/health") -Method Get -TimeoutSec 5
    Write-Host "   ✓ Health Check: $($response.status)" -ForegroundColor Green
    Write-Host "     Database: $($response.database)" -ForegroundColor Gray
    Write-Host "     Gemini: $($response.gemini)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Register User
Write-Host "2. Testing Registration Endpoint..." -ForegroundColor Yellow
$randomNum = Get-Random
$registerBody = @{
    name = "Test User $randomNum"
    email = "testuser$randomNum@example.com"
    password = "TestPassword123"
    role = "user"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri ($baseUrl + "/api/v1/auth/register") -Method Post -Body $registerBody -ContentType "application/json" -TimeoutSec 10
    Write-Host "   ✓ Registration Successful!" -ForegroundColor Green
    Write-Host "     User ID: $($response.id)" -ForegroundColor Gray
    Write-Host "     Email: $($response.email)" -ForegroundColor Gray
    Write-Host "     Role: $($response.role)" -ForegroundColor Gray
    
    $script:testEmail = $response.email
    $script:testPassword = "TestPassword123"
} catch {
    Write-Host "   ✗ Registration Failed" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "     Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    } else {
        Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    $script:testEmail = "testuser@example.com"
    $script:testPassword = "TestPassword123"
}

Write-Host ""

# Test 3: Login
Write-Host "3. Testing Login Endpoint..." -ForegroundColor Yellow
$loginBody = @{
    email = $script:testEmail
    password = $script:testPassword
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri ($baseUrl + "/api/v1/auth/login") -Method Post -Body $loginBody -ContentType "application/json" -TimeoutSec 10
    Write-Host "   ✓ Login Successful!" -ForegroundColor Green
    Write-Host "     Token Type: $($response.token_type)" -ForegroundColor Gray
    $tokenPreview = $response.access_token.Substring(0, [Math]::Min(50, $response.access_token.Length))
    Write-Host "     Access Token: ${tokenPreview}..." -ForegroundColor Gray
    
    $script:accessToken = $response.access_token
} catch {
    Write-Host "   ✗ Login Failed" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "     Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    } else {
        Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    $script:accessToken = $null
}

Write-Host ""

# Test 4: Get Current User (if logged in)
if ($script:accessToken) {
    Write-Host "4. Testing Get Current User Endpoint..." -ForegroundColor Yellow
    $headers = @{
        "Authorization" = "Bearer $($script:accessToken)"
    }
    try {
        $response = Invoke-RestMethod -Uri ($baseUrl + "/api/v1/auth/me") -Method Get -Headers $headers -TimeoutSec 10
        Write-Host "   ✓ Get User Successful!" -ForegroundColor Green
        Write-Host "     Name: $($response.name)" -ForegroundColor Gray
        Write-Host "     Email: $($response.email)" -ForegroundColor Gray
    } catch {
        Write-Host "   ✗ Get User Failed" -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host "     Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

# Test 5: List Plants
Write-Host "5. Testing List Plants Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri ($baseUrl + "/api/v1/plants/") -Method Get -TimeoutSec 10
    Write-Host "   ✓ List Plants Successful!" -ForegroundColor Green
    Write-Host "     Total Plants: $($response.total)" -ForegroundColor Gray
    Write-Host "     Page: $($response.page)" -ForegroundColor Gray
    Write-Host "     Plants Returned: $($response.plants.Count)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ List Plants Failed" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "     Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Production URLs:" -ForegroundColor Yellow
$apiUrl = $baseUrl + "/api/v1"
$healthUrl = $baseUrl + "/health"
$docsUrl = $baseUrl + "/docs"
Write-Host "  API Base: $apiUrl" -ForegroundColor White
Write-Host "  Health: $healthUrl" -ForegroundColor White
Write-Host "  Docs: $docsUrl" -ForegroundColor White
