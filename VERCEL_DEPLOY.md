# Deploy Frontend to Vercel (Recommended)

Vercel is optimized for static sites and SvelteKit. It's free and easier to set up than Railway for frontends.

## Quick Setup

### Option 1: Vercel Dashboard (Easiest)

1. **Go to [vercel.com](https://vercel.com)** and sign up/login
2. **Click "Add New Project"**
3. **Import your GitHub repository**
4. **Configure:**
   - **Framework Preset**: SvelteKit (auto-detected)
   - **Root Directory**: `Frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

5. **Environment Variables:**
   - Add: `VITE_API_URL`
   - Value: `https://your-backend-service.up.railway.app`
   - ⚠️ Use `https://` not `http://`

6. **Deploy!**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Your site will be live in ~2 minutes

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend
cd Frontend

# Deploy
vercel

# Follow prompts:
# - Set root directory: Frontend
# - Add environment variable: VITE_API_URL
```

## Advantages of Vercel

✅ **Free tier** - Generous limits  
✅ **Automatic HTTPS** - SSL certificates included  
✅ **CDN** - Fast global delivery  
✅ **Auto-deploy** - Deploys on every git push  
✅ **Preview deployments** - Test PRs before merging  
✅ **Zero config** - Works out of the box with SvelteKit  
✅ **Better for static sites** - Optimized for frontends  

## Configuration

The `Frontend/vercel.json` file is already created with proper settings. Vercel will:
- Auto-detect SvelteKit
- Build to `build` directory
- Serve static files correctly
- Handle routing for SPA

## Environment Variables

Set in Vercel Dashboard → Project → Settings → Environment Variables:
- `VITE_API_URL`: Your Railway backend URL

## Custom Domain

1. Go to Project → Settings → Domains
2. Add your domain
3. Update DNS as instructed
4. Update backend `CORS_ORIGINS` to include your domain

## Comparison: Railway vs Vercel

| Feature | Railway | Vercel |
|---------|---------|--------|
| Static Sites | ✅ Works | ✅ Optimized |
| Setup Complexity | Medium | Easy |
| Free Tier | Limited | Generous |
| CDN | ❌ | ✅ |
| Auto HTTPS | ✅ | ✅ |
| Preview Deploys | ❌ | ✅ |
| Best For | Full-stack apps | Frontends |

## Recommendation

**Use Vercel for frontend** - It's specifically designed for static sites and will give you:
- Faster deployments
- Better performance (CDN)
- Easier configuration
- Free custom domains

**Keep Railway for backend** - It's great for API services and databases.

## After Deployment

1. **Update Backend CORS:**
   - In Railway backend → Variables
   - Add your Vercel URL to `CORS_ORIGINS`:
     ```
     https://your-app.vercel.app
     ```

2. **Test:**
   - Visit your Vercel URL
   - Check browser console for errors
   - Test API connections

