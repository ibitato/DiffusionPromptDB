#!/bin/bash
# Fix Mixed Content Error in Production
# This script rebuilds the frontend with correct HTTPS configuration

set -e

echo "🔧 Fixing Mixed Content Error..."

# Navigate to project root
cd /var/www/diffusionprompt

# Ensure .env.production exists
if [ ! -f "frontend/.env.production" ]; then
    echo "📝 Creating .env.production..."
    cat > frontend/.env.production << 'ENVEOF'
# Production Environment Configuration
# DO NOT set VITE_API_URL in production - it will default to same protocol/hostname
# VITE_API_URL is intentionally NOT set here

# API Key for read-only operations (catalog/search)
VITE_API_KEY=REDACTED_API_KEY
ENVEOF
fi

# Rebuild frontend
echo "🔨 Rebuilding frontend..."
cd frontend

# Remove old build
rm -rf dist

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build for production (will use .env.production)
echo "🏗️  Building for production..."
npm run build

# Verify build
if [ ! -d "dist" ]; then
    echo "❌ Build failed - dist directory not created"
    exit 1
fi

echo "✅ Frontend rebuilt successfully"

# Restart nginx to ensure fresh content
echo "🔄 Restarting nginx..."
systemctl restart nginx

echo ""
echo "✅ Mixed Content fix applied!"
echo ""
echo "The frontend will now:"
echo "  • Use HTTPS when accessed via HTTPS"
echo "  • Automatically match the page protocol"
echo "  • No more Mixed Content errors"
echo ""
echo "Please test by accessing: https://www.diffusionprompt.net"
