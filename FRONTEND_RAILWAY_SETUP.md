# Frontend Railway Deployment Setup

## Step-by-Step Instructions

### 1. Create Frontend Service in Railway

1. In your Railway project dashboard, click **"+ New"** → **"GitHub Repo"** (or **"Empty Service"**)
2. If using GitHub Repo, select your repository
3. Name the service: `frontend` (or `barter-app-frontend`)

### 2. Configure Service Settings

Go to the frontend service → **Settings**:

#### Root Directory
- Set **Root Directory** to: `Frontend`

#### Build & Deploy
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npx serve -s build -l $PORT`
- **Output Directory**: `build` (optional, Railway will detect it)

#### Builder
- Select **Nixpacks** (Railway will auto-detect Node.js)

### 3. Set Environment Variables

Go to **Variables** tab in your frontend service:

**Required:**
- `VITE_API_URL`: Your backend URL
  - Format: `https://your-backend-service.up.railway.app`
  - Example: `https://barter-app-production.up.railway.app`
  - ⚠️ **Important**: Use `https://` not `http://`

**How to get backend URL:**
- Go to your backend service in Railway
- Copy the URL from the service overview (e.g., `backend-production-xxxx.up.railway.app`)
- Add `https://` prefix

### 4. Deploy

After configuring:
1. Railway will automatically detect changes and redeploy
2. Or manually trigger a deploy from the dashboard
3. Wait for build to complete (usually 2-5 minutes)

### 5. Verify Deployment

1. **Check Frontend URL:**
   - Your frontend will be available at: `https://your-frontend-service.up.railway.app`
   - Visit the URL in your browser

2. **Check Backend Connection:**
   - Open browser console (F12)
   - Look for any API connection errors
   - Verify `VITE_API_URL` is set correctly

3. **Test Functionality:**
   - Try logging in/signing up
   - Check if API calls are working

## Configuration Summary

✅ **Files Updated:**
- `Frontend/package.json` - Added `serve` package and `start` script
- `Frontend/railway.json` - Railway configuration

✅ **Railway Settings:**
- Root Directory: `Frontend`
- Build Command: `npm install && npm run build`
- Start Command: `npm start` (uses serve package)
- Environment Variable: `VITE_API_URL` = your backend URL

## Troubleshooting

### Build Fails
- Check that Root Directory is set to `Frontend`
- Verify `package.json` has all dependencies
- Check build logs for specific errors

### Frontend Can't Connect to Backend
- Verify `VITE_API_URL` is set correctly (with `https://`)
- Check backend is running and accessible
- Verify CORS is configured in backend to allow frontend URL

### 404 Errors on Routes
- This is normal for SPA - Railway should serve `index.html` for all routes
- The `serve -s` flag handles this (single-page app mode)

### Port Issues
- Railway automatically sets `$PORT` - don't hardcode it
- The `serve` package will use the port from `$PORT` environment variable
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file
