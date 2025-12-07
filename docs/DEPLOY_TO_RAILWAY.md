# 🚀 Railway Deployment Guide - Frontend + Backend

This guide will help you deploy both your **Frontend (SvelteKit)** and **Backend (FastAPI)** on Railway.

---

## 📋 Prerequisites

- Railway account (https://railway.app)
- GitHub repository with your code
- Your code committed and pushed to GitHub

---

## 🎯 Deployment Strategy

We'll deploy **2 services** on Railway:
1. **Backend Service** - FastAPI (already deployed)
2. **Frontend Service** - SvelteKit (new)

---

## 🔧 Step 1: Deploy Backend Service (Update Existing)

Your backend is already on Railway. Let's update its environment variables:

### Backend Environment Variables

Go to Railway → Your Backend Service → Variables

**Set these 7 variables:**

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `mysql+pymysql://avnadmin:AVNS_RxetGKQTrVxowGD84Ki@mysql-21ce443a-barterexchangeapp.h.aivencloud.com:28370/bayanihan_exchange` |
| `SSL_CA_PATH` | `aiven-ca.pem` |
| `SUPABASE_URL` | `https://gputqdaervtkhkzpscby.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwdXRxZGFlcnZ0a2hrenBzY2J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1OTAxNzIsImV4cCI6MjA4MDE2NjE3Mn0.o33xElBEpx9u15pWfjOx8brjAsmSg0_F5PBEfdg0iUo` |
| `SECRET_KEY` | `{{ secret }}` (keep as-is) |
| `FRONTEND_URL` | `https://your-frontend-service.up.railway.app` (UPDATE AFTER FRONTEND DEPLOYMENT) |
| `CORS_ORIGINS` | `https://your-frontend-service.up.railway.app` (UPDATE AFTER FRONTEND DEPLOYMENT) |

**Delete these deprecated variables:**
- ❌ `MAIL_USERNAME`
- ❌ `MAIL_PASSWORD`
- ❌ `MAIL_FROM`
- ❌ `MAIL_FROM_NAME`
- ❌ `MAIL_PORT`
- ❌ `MAIL_SERVER`

---

## 🚀 Step 2: Deploy Frontend Service (New)

### 2.1 Create New Service on Railway

1. Go to your Railway project
2. Click **"+ New"** → **"GitHub Repo"**
3. Select your `barter_app` repository
4. Railway will detect it as a Node.js app
5. Click **"Deploy"**

### 2.2 Configure Frontend Service

After the service is created:

1. Go to **Settings** → **General**
2. Set **Root Directory** to: `/Frontend`
3. Save changes

### 2.3 Set Frontend Environment Variables

Go to **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://your-backend-service.up.railway.app` (your backend URL) |

**How to get your backend URL:**
- Go to your Backend service
- Click on **Settings** → **Networking**
- Copy the **Public Domain** (e.g., `https://backend-production-xxxx.up.railway.app`)

### 2.4 Generate Public Domain for Frontend

1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy the generated URL (e.g., `https://frontend-production-yyyy.up.railway.app`)
4. This is your **Frontend URL**

---

## 🔄 Step 3: Update Backend Variables with Frontend URL

Now that you have your frontend URL:

1. Go back to your **Backend Service**
2. Go to **Variables**
3. Update these 2 variables:
   - `FRONTEND_URL` = `https://frontend-production-yyyy.up.railway.app`
   - `CORS_ORIGINS` = `https://frontend-production-yyyy.up.railway.app`
4. Save and redeploy

---

## ✅ Step 4: Verify Deployment

### Check Backend
1. Visit: `https://your-backend-service.up.railway.app/health`
2. Should return: `{"status": "ok"}`

### Check Frontend
1. Visit: `https://your-frontend-service.up.railway.app`
2. You should see your landing page
3. Try signing up/logging in to test authentication

---

## 📊 Final Configuration Summary

### Backend Service
- **Root Directory**: `/Backend` (or leave empty if not set)
- **Build Command**: Auto-detected (pip install)
- **Start Command**: Auto-detected (uvicorn)
- **Environment Variables**: 7 total

### Frontend Service
- **Root Directory**: `/Frontend`
- **Build Command**: `npm run build`
- **Start Command**: `node build`
- **Environment Variables**: 1 (`VITE_API_URL`)

---

## 🐛 Troubleshooting

### Frontend won't build
- Check **Logs** tab for errors
- Ensure Node version is 20+ (set in nixpacks.toml)
- Verify all dependencies are in package.json

### CORS errors
- Ensure `CORS_ORIGINS` in backend matches frontend URL **exactly**
- No trailing slash
- Use HTTPS not HTTP

### Backend connection fails
- Verify `VITE_API_URL` is correct
- Check backend is running in **Deployments** tab
- Ensure backend health endpoint works

### Authentication not working
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Check backend logs for Supabase connection errors

---

## 🎯 Next Steps After Deployment

1. **Update Supabase Redirect URLs**
   - Go to Supabase Dashboard → Authentication → URL Configuration
   - Add your Railway frontend URL to **Site URL** and **Redirect URLs**

2. **Test All Features**
   - User signup/login
   - Email verification
   - Password reset
   - Item CRUD operations
   - Trade functionality

3. **Monitor Logs**
   - Keep an eye on Railway logs for any errors
   - Check both frontend and backend services

4. **Optional: Custom Domain**
   - You can add your own domain in Railway → Settings → Networking

---

## 📝 Quick Reference

### Your URLs (Update these after deployment):

```
Backend URL:  https://_____________________.up.railway.app
Frontend URL: https://_____________________.up.railway.app
Health Check: https://_____________________.up.railway.app/health
```

### Railway Projects Structure:

```
📦 Your Railway Project
├── 🔧 Backend Service (FastAPI)
│   ├── Database: Aiven MySQL
│   ├── Auth: Supabase
│   └── Variables: 7
│
└── 🎨 Frontend Service (SvelteKit)
    ├── API: Points to Backend
    └── Variables: 1
```

---

**🎉 Congratulations!** Both your frontend and backend are now on Railway!

**Last Updated:** 2025-12-05
