# 🚨 QUICK FIX: Mixed Content Error

## Problem
Frontend making HTTP requests on HTTPS site → **Mixed Content Error**

## Solution (On Production Server)

```bash
# SSH into server
ssh root@77.42.30.232

# Navigate to project
cd /var/www/diffusionprompt

# Run fix script
chmod +x deploy/fix_mixed_content.sh
sudo ./deploy/fix_mixed_content.sh
```

## What It Does
1. Creates `.env.production` file (without VITE_API_URL)
2. Rebuilds frontend with automatic protocol detection
3. Restarts nginx

## Verify Fix
1. Clear browser cache completely
2. Visit: `https://www.diffusionprompt.net`
3. Open DevTools → Console
4. Should see NO "Mixed Content" errors
5. Check Network tab → API calls should use HTTPS

## Time Required
~5 minutes (rebuild + verification)

## Full Documentation
See [MIXED_CONTENT_FIX.md](./MIXED_CONTENT_FIX.md) for complete details.

---

## Manual Fix (Alternative)

If the script fails, manually do:

```bash
cd /var/www/diffusionprompt/frontend

# Create .env.production
cat > .env.production << 'EOF'
# VITE_API_URL is intentionally NOT set
VITE_API_KEY=demo-read-key-12345
EOF

# Rebuild
rm -rf dist
npm run build

# Restart nginx
sudo systemctl restart nginx
```

## Files Changed
- `frontend/src/services/api.ts` - Auto protocol detection
- `frontend/.env.production` - Production env config
- `deploy/fix_mixed_content.sh` - Fix script
