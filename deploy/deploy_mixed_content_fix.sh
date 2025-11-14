#!/bin/bash
# Deploy Mixed Content Fix to Production
# Run this locally to deploy the fix to production server

set -e

SERVER_USER="root"
SERVER_IP="77.42.30.232"
REMOTE_PATH="/var/www/diffusionprompt"
PROJECT_NAME="DiffusionPromptDB"

echo "🚀 Deploying Mixed Content Fix to Production..."
echo ""

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Create temporary tarball with just the necessary files
echo "📦 Creating deployment package..."
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/deploy"
mkdir -p "$TEMP_DIR/frontend/src/services"

# Copy necessary files
cp deploy/fix_mixed_content.sh "$TEMP_DIR/deploy/"
cp deploy/MIXED_CONTENT_FIX.md "$TEMP_DIR/deploy/"
cp deploy/QUICK_FIX_SUMMARY.md "$TEMP_DIR/deploy/"
cp frontend/src/services/api.ts "$TEMP_DIR/frontend/src/services/"
cp frontend/.env.production "$TEMP_DIR/frontend/"

# Create tarball
cd "$TEMP_DIR"
tar -czf mixed-content-fix.tar.gz deploy/ frontend/
cd -

echo "✅ Package created"
echo ""

# Upload to server
echo "📤 Uploading to server..."
scp "$TEMP_DIR/mixed-content-fix.tar.gz" "$SERVER_USER@$SERVER_IP:/tmp/"

echo "✅ Uploaded"
echo ""

# Execute on server
echo "🔧 Applying fix on server..."
ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
set -e

echo "📦 Extracting files..."
cd /var/www/diffusionprompt
tar -xzf /tmp/mixed-content-fix.tar.gz
rm /tmp/mixed-content-fix.tar.gz

echo "✅ Files extracted"
echo ""

echo "🔨 Rebuilding frontend..."
cd frontend

# Ensure .env.production is in place
if [ -f ".env.production" ]; then
    echo "✅ .env.production found"
else
    echo "❌ .env.production not found!"
    exit 1
fi

# Remove old build
rm -rf dist

# Rebuild
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Frontend rebuilt"
echo ""

echo "🔄 Restarting nginx..."
systemctl restart nginx

echo "✅ Nginx restarted"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Mixed Content fix deployed successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Clear browser cache (Ctrl+Shift+Delete)"
echo "   2. Visit: https://www.diffusionprompt.net"
echo "   3. Check DevTools Console - should see NO Mixed Content errors"
echo "   4. Verify API calls in Network tab use HTTPS"
echo ""
ENDSSH

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Local cleanup complete"
echo ""
echo "🎯 Deployment finished! Test at: https://www.diffusionprompt.net"
