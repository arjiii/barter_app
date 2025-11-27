# Fixing Railway "pip: not found" Error

## The Problem
Railway is trying to use a Dockerfile approach instead of Nixpacks, which means Python/pip isn't being installed.

## Solution Steps

### 1. Verify Root Directory in Railway Dashboard
- Go to your backend service in Railway
- Click **Settings**
- Under **Root Directory**, make sure it's set to: `Backend`
- **Save** the changes

### 2. Force Nixpacks Builder
In Railway Dashboard:
- Go to your backend service → **Settings**
- Scroll to **Build & Deploy** section
- Under **Builder**, select **Nixpacks** (not Docker)
- If you see "Auto-detect", change it to **Nixpacks**

### 3. Clear Build Cache (Important!)
- In Railway Dashboard → Backend service
- Go to **Settings** → **Build & Deploy**
- Click **Clear Build Cache**
- This forces Railway to rebuild from scratch

### 4. Verify Files Are Present
Make sure these files exist:
- ✅ `Backend/nixpacks.toml` (should have `nixPkgs = ["python311", "pip"]`)
- ✅ `Backend/requirements.txt`
- ✅ `Backend/runtime.txt`
- ✅ `Backend/Procfile` (optional, but helpful)

### 5. Redeploy
- After making changes, Railway should auto-redeploy
- Or manually trigger a redeploy from the dashboard
- Watch the build logs to verify it's using Nixpacks

## What Should Happen

When working correctly, you should see in the build logs:
```
Using Nixpacks
Detected Python project
Installing Python 3.11
Installing pip
Running: pip install -r requirements.txt
```

Instead of:
```
load build definition from Dockerfile
pip: command not found
```

## Alternative: Manual Build Configuration

If Nixpacks still doesn't work, you can manually configure:

1. In Railway Dashboard → Backend → Settings
2. Under **Build & Deploy**:
   - **Build Command**: Leave empty (let Nixpacks handle it)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `Backend`

## Still Not Working?

If you're still seeing the error:

1. **Check the build logs** - Look for what builder Railway is using
2. **Verify Root Directory** - It MUST be `Backend` (case-sensitive)
3. **Delete and recreate the service** - Sometimes Railway caches old config
4. **Check for hidden Dockerfile** - Make sure there's no Dockerfile in your repo that Railway might be detecting

## Files Created/Updated

- ✅ `nixpacks.toml` (root) - For Railway to detect at repo level
- ✅ `Backend/nixpacks.toml` - For Railway when root directory is Backend
- ✅ `Backend/Procfile` - Fallback start command
- ✅ `Backend/runtime.txt` - Python version specification
- ✅ `railway.json` - Railway configuration

