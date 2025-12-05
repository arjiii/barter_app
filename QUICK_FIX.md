# 🚨 QUICK FIX - Update These NOW

## Railway Environment Variables

Go to: https://railway.app → Your Project → Variables

### 1. UPDATE THIS (Critical - Fixes CORS):
```
CORS_ORIGINS = https://barterv5app.vercel.app
```

### 2. OPTIONALLY REMOVE THESE (No longer needed):
- `MAIL_USERNAME`
- `MAIL_PASSWORD`  
- `MAIL_FROM`
- `MAIL_FROM_NAME`
- `MAIL_PORT`
- `MAIL_SERVER`

## That's It!

Once Railway redeploys (~2 minutes), your CORS errors will be gone! ✅

Test at: https://barterv5app.vercel.app
