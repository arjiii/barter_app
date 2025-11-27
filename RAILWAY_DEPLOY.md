# Railway Deployment Guide

## Fixing the "pip: not found" Error

The error occurs because Railway isn't detecting your Python project. Here's how to fix it:

### Solution 1: Set Root Directory in Railway (Recommended)

1. **In Railway Dashboard:**
   - Go to your backend service
   - Click on "Settings"
   - Find "Root Directory" setting
   - Set it to: `Backend`
   - Save changes

2. **Verify Configuration Files:**
   - Make sure `Backend/nixpacks.toml` exists (already created)
   - Make sure `Backend/runtime.txt` exists (already created)
   - Make sure `Backend/requirements.txt` exists (already exists)

3. **Redeploy:**
   - Railway should automatically redeploy
   - Or trigger a manual redeploy from the dashboard

### Solution 2: Use Railway.json (Alternative)

If Solution 1 doesn't work, the `railway.json` file at the root should help Railway detect the project type. However, you still need to set the root directory to `Backend` in Railway settings.

### Solution 3: Manual Build Configuration

If the above doesn't work:

1. In Railway dashboard → Backend service → Settings
2. Under "Build & Deploy":
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `Backend`

## Complete Railway Setup Steps

### 1. Configure Backend Service

**Settings to configure:**
- **Root Directory**: `Backend`
- **Build Command**: `pip install -r requirements.txt` (or leave empty to use nixpacks.toml)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
- `DATABASE_URL`: Your MySQL connection string
  - Format: `mysql+pymysql://user:password@host:port/database`
  - For Railway MySQL: Use the connection string from Railway's database service
- `SECRET_KEY`: Generate a random secret key
- `CORS_ORIGINS`: Your frontend URL (e.g., `https://your-frontend.up.railway.app`)

### 2. Configure Frontend Service (if deploying)

**Settings:**
- **Root Directory**: `Frontend`
- **Build Command**: `npm install && npm run build`
- **Output Directory**: `build`

**Environment Variables:**
- `VITE_API_URL`: Your backend URL (e.g., `https://your-backend.up.railway.app`)

### 3. Database Setup

**Option A: Railway MySQL**
- Create a MySQL service in Railway
- Railway will provide a connection string
- Set it as `DATABASE_URL` in backend environment variables

**Option B: External MySQL**
- Use PlanetScale, Aiven, or another MySQL provider
- Set connection string as `DATABASE_URL`

**After database is set up:**
- Run the schema from `Backend/mysql/schema.sql` in your database
- Or the backend will attempt to create tables on startup

## Verification

After deployment:

1. **Check Backend Health:**
   ```
   https://your-backend.up.railway.app/health
   ```
   Should return: `{"status": "ok"}`

2. **Check Database Connection:**
   ```
   https://your-backend.up.railway.app/debug/db-info
   ```
   Should show database information

3. **Test Frontend:**
   - Visit your frontend URL
   - Check browser console for errors
   - Test login/signup functionality

## Troubleshooting

### "pip: not found" Error
- ✅ Set Root Directory to `Backend` in Railway settings
- ✅ Ensure `Backend/nixpacks.toml` exists
- ✅ Ensure `Backend/requirements.txt` exists

### "Module not found" Errors
- Check that all dependencies are in `requirements.txt`
- Verify build completed successfully
- Check build logs for installation errors

### Database Connection Errors
- Verify `DATABASE_URL` is set correctly
- Check database is running and accessible
- For external databases, ensure Railway's IPs are whitelisted

### CORS Errors
- Set `CORS_ORIGINS` to include your frontend URL
- No trailing slashes in URLs
- Use `https://` not `http://`

## Quick Fix Checklist

- [ ] Root Directory set to `Backend` in Railway
- [ ] `Backend/nixpacks.toml` exists
- [ ] `Backend/runtime.txt` exists
- [ ] `Backend/requirements.txt` exists
- [ ] Environment variables set (DATABASE_URL, SECRET_KEY, CORS_ORIGINS)
- [ ] Database is running and accessible
- [ ] Redeployed after configuration changes

