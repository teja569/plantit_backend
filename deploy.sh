#!/bin/bash
# Render Deployment Script
# This script helps deploy to Render without GitHub

set -e  # Exit on error

echo "🚀 Render Deployment Script"
echo "=========================="
echo ""

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found!"
    echo ""
    echo "Install it with:"
    echo "  npm install -g render-cli"
    echo ""
    echo "Or visit: https://github.com/renderinc/cli"
    exit 1
fi

echo "✅ Render CLI found"
echo ""

# Check if logged in
if ! render whoami &> /dev/null; then
    echo "⚠️  Not logged in to Render"
    echo "Logging in..."
    render login
fi

echo "✅ Logged in to Render"
echo ""

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found!"
    echo "Please ensure render.yaml exists in the current directory"
    exit 1
fi

echo "✅ render.yaml found"
echo ""

# Check environment variables
echo "📋 Checking environment variables..."
echo ""
echo "Required variables:"
echo "  - SECRET_KEY"
echo "  - DATABASE_URL or PRISMA_DATABASE_URL"
echo "  - GEMINI_API_KEY"
echo "  - ALLOWED_ORIGINS"
echo ""

read -p "Have you set all environment variables in Render Dashboard? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Please set environment variables in Render Dashboard first"
    echo "   Go to: https://dashboard.render.com → Your Service → Environment"
    exit 1
fi

echo ""
echo "🚀 Starting deployment..."
echo ""

# Deploy
if render deploy; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "Next steps:"
    echo "  1. Check your service in Render Dashboard"
    echo "  2. Test the /health endpoint"
    echo "  3. Update your frontend to use the new API URL"
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Check the logs above for errors"
    exit 1
fi

