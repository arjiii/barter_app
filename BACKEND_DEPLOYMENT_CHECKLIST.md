# Backend Deployment Checklist for Railway

## ✅ Step 1: Create Backend Service in Railway

1. Go to [Railway Dashboard](https://railway.app)
2. Click **"New Project"** or select your existing project
3. Click **"New Service"** → **"GitHub Repo"**
4. Select your `barter_app` repository
5. Railway will create a service - **rename it to "Backend"**

## ✅ Step 2: Configure Root Directory

**CRITICAL:** Railway must know to look in the `Backend` folder.

1. In Railway Dashboard → Click on your **Backend** service
2. Go to **Settings** tab
3. Scroll to **"Root Directory"**
4. Set it to: `Backend`
5. Click **"Save"**

## ✅ Step 3: Add MySQL Database

1. In Railway Dashboard → Click **"New Service"**
2. Select **"Database"** → **"Add MySQL"**
3. Railway will create a MySQL database
4. **Copy the connection string** (you'll need it in the next step)

## ✅ Step 4: Set Environment Variables

In Railway Dashboard → Backend service → **Variables** tab, add:

### Required Variables:

```
DATABASE_URL=mysql+pymysql://user:password@host:port/database
```
- Replace with your Railway MySQL connection string
- Format: `mysql+pymysql://root:PASSWORD@MYSQLHOST:MYSQLPORT/railway`
- Railway provides this in the MySQL service → **Variables** → `MYSQL_URL` or `DATABASE_URL`

```
SECRET_KEY=your-super-secret-key-here-change-this
```
- Generate a random string (e.g., use: `openssl rand -hex 32`)
- Or use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

```
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.up.railway.app
```
- Replace with your actual frontend URL(s)
- If using Vercel: `https://your-app.vercel.app`
- If using Railway for frontend: `https://your-frontend.up.railway.app`
- **Important:** Use `https://` not `http://`
- **No trailing slashes**
- Separate multiple URLs with commas

### Optional Variables (if using external MySQL with SSL):

```
SSL_CA_PATH=/path/to/ca-cert.pem
```
or

```
SSL_CA_PEM=-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----
```

## ✅ Step 5: Initialize Database Schema

After the backend is deployed:

1. Go to your MySQL service in Railway
2. Click **"Query"** tab (or use Railway CLI)
3. Run the SQL from `Backend/mysql/schema.sql`
4. Or the backend will auto-create tables on first startup (if permissions allow)

## ✅ Step 6: Deploy

1. Railway should auto-deploy when you push to GitHub
2. Or manually trigger: **Backend service** → **"Deploy"** → **"Redeploy"**
3. Watch the build logs for errors

## ✅ Step 7: Verify Deployment

### Test Health Endpoint:
```
https://your-backend.up.railway.app/health
```
Should return: `{"status": "ok"}`

### Test Database Connection:
```
https://your-backend.up.railway.app/debug/db-info
```
Should show database information

## 🔧 Troubleshooting

### Error: "pip: not found" or "Python not found"
- ✅ **Root Directory** must be set to `Backend` in Railway settings
- ✅ Verify `Backend/nixpacks.toml` exists
- ✅ Verify `Backend/runtime.txt` exists (should contain `python-3.11`)

### Error: "Module not found"
- ✅ Check `Backend/requirements.txt` has all dependencies
- ✅ Check build logs - did `pip install` complete successfully?

### Error: "Database connection failed"
- ✅ Verify `DATABASE_URL` is set correctly
- ✅ Check MySQL service is running in Railway
- ✅ Verify connection string format: `mysql+pymysql://user:password@host:port/database`
- ✅ For external databases, ensure Railway IPs are whitelisted

### Error: "CORS error" in frontend
- ✅ Set `CORS_ORIGINS` to your frontend URL
- ✅ Use `https://` not `http://`
- ✅ No trailing slashes
- ✅ Restart backend after changing environment variables

### Build succeeds but service won't start
- ✅ Check `PORT` environment variable (Railway sets this automatically)
- ✅ Verify start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ Check logs for Python errors

## 📋 Quick Verification Checklist

- [ ] Backend service created in Railway
- [ ] Root Directory set to `Backend`
- [ ] MySQL database service added
- [ ] `DATABASE_URL` environment variable set
- [ ] `SECRET_KEY` environment variable set
- [ ] `CORS_ORIGINS` environment variable set (with frontend URL)
- [ ] Database schema initialized (or auto-created)
- [ ] Backend deployed successfully
- [ ] `/health` endpoint returns `{"status": "ok"}`
- [ ] `/debug/db-info` shows database connection

## 🔗 Next Steps

After backend is deployed:

1. **Update Frontend Environment Variable:**
   - In Vercel (or Railway frontend service)
   - Set `VITE_API_URL` to your backend URL: `https://your-backend.up.railway.app`
   - Redeploy frontend

2. **Test Full Stack:**
   - Visit frontend
   - Try signing up
   - Check browser console for errors
   - Verify API calls are working

