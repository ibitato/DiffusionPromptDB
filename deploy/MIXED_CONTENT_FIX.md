# Mixed Content Error Fix

## Problem

When deploying to production with HTTPS, the frontend was making HTTP requests to the API, causing "Mixed Content" errors:

```
Mixed Content: The page at 'https://www.diffusionprompt.net/prompts' was loaded over HTTPS, 
but requested an insecure XMLHttpRequest endpoint 'http://www.diffusionprompt.net/api/v1/prompts/...'. 
This request has been blocked; the content must be served over HTTPS.
```

## Root Cause

The frontend was using a hardcoded `VITE_API_URL` environment variable that specified `http://` protocol. When building for production, this HTTP URL was baked into the build, causing the Mixed Content error when accessed over HTTPS.

## Solution

### 1. Smart API URL Detection

Modified `frontend/src/services/api.ts` to automatically detect and use the same protocol as the page:

```typescript
// API Base URL - defaults to same protocol/hostname as the frontend
// Only override with VITE_API_URL in development
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'production' 
    ? `${window.location.protocol}//${window.location.hostname}/api/v1`
    : 'http://localhost:8000/api/v1');
```

This ensures:
- **Development**: Uses `http://localhost:8000/api/v1` by default
- **Production**: Automatically uses the same protocol and hostname as the page
- **Custom Override**: Can still be overridden with `VITE_API_URL` in development

### 2. Production Environment File

Created `frontend/.env.production`:

```bash
# Production Environment Configuration
# DO NOT set VITE_API_URL in production - it will default to same protocol/hostname
# VITE_API_URL is intentionally NOT set here

# API Key for read-only operations (catalog/search)
VITE_API_KEY=demo-read-key-12345
```

**Important**: `VITE_API_URL` is intentionally NOT set in production to allow automatic protocol detection.

## Deployment

### Quick Fix (On Server)

If you've already deployed and need to fix the Mixed Content error:

```bash
# On the production server
cd /var/www/diffusionprompt
chmod +x deploy/fix_mixed_content.sh
sudo ./deploy/fix_mixed_content.sh
```

This script will:
1. Create/verify `.env.production` file
2. Rebuild the frontend with correct configuration
3. Restart nginx to serve the new build

### Full Deployment

For fresh deployments or rebuilding from source:

```bash
# 1. Build frontend locally with production config
cd frontend
npm run build  # Will use .env.production automatically

# 2. Deploy the build
# ... copy to server ...

# 3. Restart nginx
sudo systemctl restart nginx
```

## Verification

After applying the fix, verify it's working:

1. **Clear browser cache** (important!)
2. Access your site via HTTPS: `https://www.diffusionprompt.net`
3. Open browser DevTools → Console
4. Check for errors - should see NO "Mixed Content" errors
5. Verify API requests are using HTTPS:
   - DevTools → Network tab
   - Filter by "api"
   - Check request URLs start with `https://`

## Testing Different Scenarios

### Local Development
```bash
cd frontend
npm run dev
# Should use http://localhost:8000/api/v1
```

### Production HTTPS
```
Access: https://www.diffusionprompt.net
API calls: https://www.diffusionprompt.net/api/v1
✓ No Mixed Content errors
```

### Production HTTP (fallback)
```
Access: http://www.diffusionprompt.net
API calls: http://www.diffusionprompt.net/api/v1
✓ Works, but will redirect to HTTPS
```

## Files Modified

1. `frontend/src/services/api.ts` - Smart protocol detection
2. `frontend/.env.production` - Production environment config
3. `deploy/fix_mixed_content.sh` - Deployment fix script
4. `deploy/MIXED_CONTENT_FIX.md` - This documentation

## Prevention

To prevent this issue in future deployments:

1. **Never** hardcode HTTP protocol in production builds
2. **Always** use `.env.production` for production-specific config
3. **Test** HTTPS locally before deploying (use mkcert or similar)
4. **Verify** in browser DevTools that all requests use HTTPS

## Troubleshooting

### Issue: Still seeing HTTP requests after fix

**Solution**: Clear browser cache completely:
```javascript
// In browser console
localStorage.clear();
sessionStorage.clear();
location.reload(true);
```

### Issue: API requests fail with CORS errors

**Solution**: Verify nginx is properly proxying API requests:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

Check nginx config has correct proxy settings:
```nginx
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Issue: Build fails

**Solution**: Ensure all dependencies are installed:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Related Issues

- Browser Mixed Content Policy: https://developer.mozilla.org/en-US/docs/Web/Security/Mixed_content
- Vite Environment Variables: https://vitejs.dev/guide/env-and-mode.html
- Nginx SSL/TLS Configuration: https://nginx.org/en/docs/http/ngx_http_ssl_module.html

## Date
Fixed: November 14, 2025

## Author
Fixed by AI Assistant following security best practices
