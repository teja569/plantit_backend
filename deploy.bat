@echo off
REM Render Deployment Script for Windows
REM This script helps deploy to Render without GitHub

echo 🚀 Render Deployment Script
echo ==========================
echo.

REM Check if Render CLI is installed (try both render and render-cli)
where render-cli >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set RENDER_CMD=render-cli
    goto :render_found
)

REM Try npx as fallback
where npx >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set RENDER_CMD=npx render-cli
    goto :render_found
)

echo ❌ Render CLI not found!
echo.
echo Install it with:
echo   npm install -g render-cli
echo.
echo Or use npx (no installation needed):
echo   npx render-cli login
echo.
echo Or visit: https://github.com/renderinc/cli
exit /b 1

:render_found
echo ✅ Render CLI found (using: %RENDER_CMD%)
echo.

REM Check if logged in
%RENDER_CMD% whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Not logged in to Render
    echo Logging in...
    %RENDER_CMD% login
)

echo ✅ Logged in to Render
echo.

REM Check if render.yaml exists
if not exist "render.yaml" (
    echo ❌ render.yaml not found!
    echo Please ensure render.yaml exists in the current directory
    exit /b 1
)

echo ✅ render.yaml found
echo.

REM Check environment variables
echo 📋 Checking environment variables...
echo.
echo Required variables:
echo   - SECRET_KEY
echo   - DATABASE_URL or PRISMA_DATABASE_URL
echo   - GEMINI_API_KEY
echo   - ALLOWED_ORIGINS
echo.

set /p REPLY="Have you set all environment variables in Render Dashboard? (y/n) "
if /i not "%REPLY%"=="y" (
    echo ⚠️  Please set environment variables in Render Dashboard first
    echo    Go to: https://dashboard.render.com → Your Service → Environment
    exit /b 1
)

echo.
echo 🚀 Starting deployment...
echo.

REM Deploy
%RENDER_CMD% deploy
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Deployment successful!
    echo.
    echo Next steps:
    echo   1. Check your service in Render Dashboard
    echo   2. Test the /health endpoint
    echo   3. Update your frontend to use the new API URL
) else (
    echo.
    echo ❌ Deployment failed!
    echo Check the logs above for errors
    exit /b 1
)

