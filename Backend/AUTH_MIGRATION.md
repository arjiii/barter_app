# Authentication Migration to Supabase

## Changes Made

### Backend Changes

1. **Removed legacy `/auth/*` endpoints**
   - Old `app/routers/auth.py` is now deprecated
   - All authentication now uses `/supabase-auth/*` endpoints

2. **New Supabase Auth Endpoints** (`/supabase-auth/*`)
   - `POST /supabase-auth/signup` - Sign up with Supabase (sends verification email automatically)
   - `POST /supabase-auth/confirm` - Confirm email after clicking verification link
   - `POST /supabase-auth/login` - Login with email/password
   - `POST /supabase-auth/forgot-password` - Request password reset (Supabase sends email)
   - `POST /supabase-auth/reset-password` - Reset password with token
   - `GET /supabase-auth/check-email/{email}` - Check email verification status

3. **Removed Email Service Dependencies**
   - No longer need `MAIL_*` environment variables
   - Supabase handles all email sending (verification, password reset)

### Frontend Changes Needed

Update `authService.ts` to use new endpoints:

```typescript
// OLD (deprecated)
const res = await fetch(`${API_BASE_URL}/auth/signup`, ...)
const res = await fetch(`${API_BASE_URL}/auth/login`, ...)
const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, ...)

// NEW (use these)
const res = await fetch(`${API_BASE_URL}/supabase-auth/signup`, ...)
const res = await fetch(`${API_BASE_URL}/supabase-auth/login`, ...)
const res = await fetch(`${API_BASE_URL}/supabase-auth/forgot-password`, ...)
```

### Environment Variables

#### ❌ No Longer Needed (can be removed from Railway):
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_FROM`
- `MAIL_FROM_NAME`
- `MAIL_PORT`
- `MAIL_SERVER`

#### ✅ Still Required:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ORIGINS` (UPDATE THIS! See below)

### IMPORTANT: Update CORS_ORIGINS

**In Railway, update `CORS_ORIGINS` to:**
```
https://barterv5app.vercel.app
```

Or for both local dev and production:
```
http://localhost:5173,https://barterv5app.vercel.app
```

## Benefits of This Change

✅ **Simpler Architecture** - One auth system instead of two  
✅ **Better Email Delivery** - Supabase handles email infrastructure  
✅ **No SMTP Configuration** - No need to manage Gmail app passwords  
✅ **More Reliable** - Supabase's email service is production-ready  
✅ **Less Code to Maintain** - Removed custom email service  

## Migration Steps

### 1. Backend (Already Done ✅)
- [x] Added password reset to supabase_auth.py
- [x] Removed auth.router from main.py
- [x] Removed email_service dependencies

### 2. Frontend (TODO)
- [ ] Update authService.ts to use `/supabase-auth/*` endpoints
- [ ] Test signup flow
- [ ] Test login flow
- [ ] Test password reset flow

### 3. Railway Environment (TODO)
- [ ] Update `CORS_ORIGINS` to `https://barterv5app.vercel.app`
- [ ] Optionally remove `MAIL_*` variables
- [ ] Redeploy

### 4. Testing Checklist
- [ ] User can sign up and receive verification email
- [ ] User can verify email and login
- [ ] User can request password reset
- [ ] User can reset password via email link
- [ ] CORS errors are resolved

## Rollback Plan

If you need to rollback:
1. Uncomment `auth` import in `main.py` line 7
2. Add back `app.include_router(auth.router)` in main.py
3. Frontend can use old `/auth/*` endpoints
