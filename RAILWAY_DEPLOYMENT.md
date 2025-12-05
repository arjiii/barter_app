# Railway Deployment Configuration Guide

## ✅ Required Environment Variables

Copy these **exact** values to your Railway service variables:

### 1. Database Configuration
```
DATABASE_URL=mysql+pymysql://avnadmin:AVNS_RxetGKQTrVxowGD84Ki@mysql-21ce443a-barterexchangeapp.h.aivencloud.com:28370/bayanihan_exchange
```

```
SSL_CA_PATH=aiven-ca.pem
```

### 2. Supabase Configuration
```
SUPABASE_URL=https://gputqdaervtkhkzpscby.supabase.co
```

```
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwdXRxZGFlcnZ0a2hrenBzY2J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1OTAxNzIsImV4cCI6MjA4MDE2NjE3Mn0.o33xElBEpx9u15pWfjOx8brjAsmSg0_F5PBEfdg0iUo
```

### 3. App Configuration
```
SECRET_KEY=dev-secret-key-change-in-production
```

```
FRONTEND_URL=https://barterv5app.vercel.app
```

### 4. CORS Configuration ⚠️ CRITICAL FIX NEEDED
**Current (WRONG):**
```
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:3000,http://127.0.0.1:3000
```

**Update to (CORRECT):**
```
CORS_ORIGINS=https://barterv5app.vercel.app
```

---

## ❌ Variables to REMOVE from Railway

These variables are **no longer needed** with Supabase authentication. You should **DELETE** them from your Railway service:

- ❌ `MAIL_USERNAME`
- ❌ `MAIL_PASSWORD`
- ❌ `MAIL_FROM`
- ❌ `MAIL_FROM_NAME`
- ❌ `MAIL_PORT`
- ❌ `MAIL_SERVER`

---

## 🔧 How to Update Railway Variables

1. Go to your Railway project: https://railway.app
2. Click on your **Backend service**
3. Go to **"Variables"** tab
4. **Update** `CORS_ORIGINS` to: `https://barterv5app.vercel.app`
5. **Delete** all MAIL_* variables (they're deprecated)
6. Verify all other variables match the list above
7. Click **"Deploy"** or wait for auto-redeploy

---

## 📋 Complete Variable Checklist

Use this checklist to verify your Railway configuration:

- [ ] `DATABASE_URL` - MySQL connection string
- [ ] `SSL_CA_PATH` - Set to `aiven-ca.pem`
- [ ] `SUPABASE_URL` - Supabase project URL
- [ ] `SUPABASE_ANON_KEY` - Supabase anonymous key
- [ ] `SECRET_KEY` - Application secret key
- [ ] `FRONTEND_URL` - Production frontend URL
- [ ] `CORS_ORIGINS` - **ONLY** production frontend URL (no localhost)
- [ ] All `MAIL_*` variables **removed**

---

## 🚨 Common Issues & Fixes

### Issue: CORS errors in production
**Fix:** Make sure `CORS_ORIGINS` is set to **exactly** `https://barterv5app.vercel.app` with NO trailing slash or extra URLs

### Issue: Authentication not working
**Fix:** Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct and have no extra spaces

### Issue: Database connection errors
**Fix:** Ensure `DATABASE_URL` and `SSL_CA_PATH` are both set correctly

---

## 🎯 Next Steps After Updating

1. Deploy the changes to Railway
2. Wait for deployment to complete (~2-3 minutes)
3. Test your frontend at https://barterv5app.vercel.app
4. Check Railway logs for any errors
5. Verify authentication flow works (signup/login)

---

**Last Updated:** 2025-12-05
**Backend URL:** Check Railway dashboard for your deployed URL
**Frontend URL:** https://barterv5app.vercel.app
