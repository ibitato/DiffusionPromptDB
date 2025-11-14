#!/bin/bash
# Deploy Force HTTPS Fix - Solución definitiva para Mixed Content

set -e

SERVER_USER="root"
SERVER_IP="REDACTED_SERVER_IP"
REMOTE_PATH="/var/www/diffusionprompt"

echo "🚀 DEPLOYING FORCE HTTPS FIX TO PRODUCTION"
echo "==========================================="
echo ""

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/deploy"
mkdir -p "$TEMP_DIR/frontend/src/services"

# Copy all necessary files
cp deploy/diagnose_mixed_content.sh "$TEMP_DIR/deploy/"
cp deploy/force_https_rebuild.sh "$TEMP_DIR/deploy/"
cp frontend/src/services/api.ts "$TEMP_DIR/frontend/src/services/"
cp frontend/.env.production "$TEMP_DIR/frontend/"

# Create tarball
cd "$TEMP_DIR"
tar -czf force-https-fix.tar.gz deploy/ frontend/
cd -

echo "✅ Package created"
echo ""

# Upload to server
echo "📤 Uploading to server..."
scp "$TEMP_DIR/force-https-fix.tar.gz" "$SERVER_USER@$SERVER_IP:/tmp/"

echo "✅ Uploaded"
echo ""

# Execute on server
echo "🔧 Executing fix on server..."
ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
set -e

echo ""
echo "📦 Extracting files..."
cd /var/www/diffusionprompt
tar -xzf /tmp/force-https-fix.tar.gz
rm /tmp/force-https-fix.tar.gz

# Make scripts executable
chmod +x deploy/diagnose_mixed_content.sh
chmod +x deploy/force_https_rebuild.sh

echo "✅ Files extracted and made executable"
echo ""

echo "=============================================="
echo "🔍 RUNNING DIAGNOSIS FIRST..."
echo "=============================================="
./deploy/diagnose_mixed_content.sh
echo ""

echo "=============================================="
echo "🔧 EXECUTING FORCE HTTPS REBUILD..."
echo "=============================================="
./deploy/force_https_rebuild.sh
echo ""

echo "=============================================="
echo "🔍 RUNNING POST-FIX DIAGNOSIS..."
echo "=============================================="
echo ""
echo "📊 POST-FIX VERIFICATION:"
echo ""
echo "Checking for HTTP references in new build:"
if grep -r "http://www.diffusionprompt.net" /var/www/diffusionprompt/frontend/dist/ 2>/dev/null | head -1; then
    echo "⚠️ WARNING: HTTP references still found!"
    echo "Manual intervention may be needed."
else
    echo "✅ No HTTP references found in build (GOOD!)"
fi
echo ""

echo "Checking API configuration:"
grep -A 2 "API_BASE_URL" /var/www/diffusionprompt/frontend/src/services/api.ts | head -5
echo ""

echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "🎉 Force HTTPS fix has been deployed!"
echo ""
echo "📝 IMPORTANT - Manual steps required:"
echo "   1. Clear ALL browser data for diffusionprompt.net"
echo "      - Chrome: Settings > Privacy > Clear browsing data"
echo "      - Select: All time, Cookies, Cache"
echo "   2. Open in Incognito/Private mode"
echo "   3. Visit: https://www.diffusionprompt.net"
echo "   4. Open DevTools (F12) immediately"
echo "   5. Check Console for [API Config] log"
echo "      - Should show: apiUrl: 'https://www.diffusionprompt.net/api/v1'"
echo "   6. Check Network tab"
echo "      - All API calls should use HTTPS"
echo ""
echo "If you still see Mixed Content errors:"
echo "   - The browser might be caching old JavaScript"
echo "   - Try a different browser or device"
echo "   - Check CloudFlare or CDN cache if applicable"
echo ""
ENDSSH

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Local cleanup complete"
echo ""
echo "=============================================="
echo "🎯 DEPLOYMENT FINISHED!"
echo "=============================================="
echo ""
echo "Test at: https://www.diffusionprompt.net"
echo ""
echo "If the problem persists after clearing cache:"
echo "  1. SSH to server: ssh $SERVER_USER@$SERVER_IP"
echo "  2. Run diagnosis: cd /var/www/diffusionprompt && ./deploy/diagnose_mixed_content.sh"
echo "  3. Check the output for any remaining HTTP references"
