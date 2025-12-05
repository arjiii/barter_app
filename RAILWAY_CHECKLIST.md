# ✅ Railway Deployment Checklist

Use this checklist to deploy both services to Railway.

---

## 🔧 Backend Service (Update Existing)

### Step 1: Clean Up Variables
- [ ] Delete `MAIL_USERNAME`
- [ ] Delete `MAIL_PASSWORD`
- [ ] Delete `MAIL_FROM`
- [ ] Delete `MAIL_FROM_NAME`
- [ ] Delete `MAIL_PORT`
- [ ] Delete `MAIL_SERVER`

### Step 2: Verify Core Variables
- [ ] `DATABASE_URL` is set correctly
- [ ] `SSL_CA_PATH` = `aiven-ca.pem`
- [ ] `SUPABASE_URL` is set correctly
- [ ] `SUPABASE_ANON_KEY` is set correctly
- [ ] `SECRET_KEY` is set (keep as secret)

### Step 3: Get Backend URL
- [ ] Go to Backend Service → Settings → Networking
- [ ] Copy the Public Domain URL
- [ ] Save it: `_________________________________`

---

## 🎨 Frontend Service (New Deployment)

### Step 1: Create New Service
- [ ] Click "+ New" on Railway dashboard
- [ ] Select "GitHub Repo"
- [ ] Choose your `barter_app` repository
- [ ] Let it auto-deploy

### Step 2: Configure Service
- [ ] Go to Settings → General
- [ ] Set Root Directory to: `/Frontend`
- [ ] Save changes

### Step 3: Add Environment Variable
- [ ] Go to Variables tab
- [ ] Add `VITE_API_URL` = (your backend URL from above)
- [ ] Example: `https://backend-production-xxxx.up.railway.app`

### Step 4: Generate Public Domain
- [ ] Go to Settings → Networking
- [ ] Click "Generate Domain"
- [ ] Copy the URL
- [ ] Save it: `_________________________________`

---

## 🔄 Final Updates

### Update Backend with Frontend URL
- [ ] Go back to Backend Service
- [ ] Go to Variables tab
- [ ] Update `FRONTEND_URL` = (your frontend URL)
- [ ] Update `CORS_ORIGINS` = (your frontend URL)
- [ ] Save and wait for redeploy

---

## ✅ Verification

### Test Backend
- [ ] Visit: `https://your-backend.up.railway.app/health`
- [ ] Should see: `{"status": "ok"}`

### Test Frontend
- [ ] Visit: `https://your-frontend.up.railway.app`
- [ ] Landing page loads correctly
- [ ] No console errors
- [ ] Try signup/login

### Test Authentication
- [ ] Create new account
- [ ] Receive verification email
- [ ] Verify email with OTP
- [ ] Login successfully
- [ ] Update profile

---

## 🎯 Post-Deployment

### Supabase Configuration
- [ ] Go to Supabase Dashboard
- [ ] Authentication → URL Configuration
- [ ] Add frontend URL to "Site URL"
- [ ] Add frontend URL to "Redirect URLs"
- [ ] Save changes

### Monitor Services
- [ ] Check Backend logs for errors
- [ ] Check Frontend logs for errors
- [ ] Test all major features
- [ ] Verify database connections

---

## 📊 Final Summary

Once complete, you should have:

✅ **2 Railway Services**
- Backend (FastAPI)
- Frontend (SvelteKit)

✅ **Backend Variables (7 total)**
- DATABASE_URL
- SSL_CA_PATH
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SECRET_KEY
- FRONTEND_URL
- CORS_ORIGINS

✅ **Frontend Variables (1 total)**
- VITE_API_URL

✅ **Both Services Running**
- Backend health check works
- Frontend loads correctly
- Authentication works end-to-end

---

**🎉 Deployment Complete!**

Your app is now fully hosted on Railway with both frontend and backend on the same platform.

**Estimated Time:** 15-20 minutes
