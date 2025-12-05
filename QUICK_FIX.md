# 🚨 URGENT: Railway Variables to Update RIGHT NOW

## ⚠️ CRITICAL FIX - Update This Variable

### CORS_ORIGINS
**Current Value (WRONG):**
```
http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:3000,http://127.0.0.1:3000
```

**Change To (CORRECT):**
```
https://barterv5app.vercel.app
```

**Why:** The current value has localhost URLs which don't work in production and will cause CORS errors.

---

## ❌ DELETE These Variables

Go to Railway > Your Service > Variables > Delete these:

1. ❌ `MAIL_USERNAME`
2. ❌ `MAIL_PASSWORD`
3. ❌ `MAIL_FROM`
4. ❌ `MAIL_FROM_NAME`
5. ❌ `MAIL_PORT`
6. ❌ `MAIL_SERVER`

**Why:** These are no longer used. Supabase handles all email functionality.

---

## ✅ Verify These Are Correct

Make sure these variables exist and have the correct values:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `mysql+pymysql://avnadmin:AVNS_RxetGKQTrVxowGD84Ki@mysql-21ce443a-barterexchangeapp.h.aivencloud.com:28370/bayanihan_exchange` |
| `SSL_CA_PATH` | `aiven-ca.pem` |
| `SUPABASE_URL` | `https://gputqdaervtkhkzpscby.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (long token) |
| `SECRET_KEY` | (your secret - keep it secret!) |
| `FRONTEND_URL` | `https://barterv5app.vercel.app` |

---

## 📝 How to Update on Railway

1. Go to: https://railway.app
2. Select your **backend service**
3. Click **"Variables"** tab
4. **Update** `CORS_ORIGINS` 
5. **Delete** all `MAIL_*` variables
6. Click **"Deploy"** (or it will auto-deploy)
7. Wait 2-3 minutes for deployment

---

## ✅ Final Checklist

After updating, you should have **ONLY** these 7 variables:

- [ ] DATABASE_URL
- [ ] SSL_CA_PATH
- [ ] SUPABASE_URL
- [ ] SUPABASE_ANON_KEY
- [ ] SECRET_KEY
- [ ] FRONTEND_URL
- [ ] CORS_ORIGINS

**Total: 7 variables** (no more MAIL_* variables!)
