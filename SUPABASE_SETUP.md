# Supabase Auth Integration Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Free Supabase Account
1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email
4. Create a new project:
   - **Name**: `barter-app` (or any name)
   - **Database Password**: (save this - you'll need it)
   - **Region**: Choose closest to you
   - Click "Create new project" (takes ~2 minutes)

### Step 2: Get Your Credentials
1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (long string starting with `eyJ...`)

### Step 3: Add to Your .env File
Create or update `Backend/.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Existing config
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/bayanihan_exchange
SECRET_KEY=dev-secret-key-change-in-production
FRONTEND_URL=http://localhost:5173
```

### Step 4: Enable Email Auth in Supabase
1. In Supabase dashboard → **Authentication** → **Providers**
2. Make sure **Email** is enabled (it should be by default)
3. Scroll down to **Email Templates**
4. Customize the "Confirm signup" email template (optional):
   ```html
   <h2>Welcome to Bayanihan Exchange!</h2>
   <p>Click the link below to verify your email:</p>
   <p><a href="{{ .ConfirmationURL }}">Verify Email</a></p>
   ```

### Step 5: Configure Email Settings (Optional but Recommended)
By default, Supabase sends emails from their domain. For production:

1. Go to **Settings** → **Auth** → **SMTP Settings**
2. Use your own SMTP (Gmail, SendGrid, etc.)
3. Or use Supabase's default (works fine for testing)

---

## 📋 How It Works

### New Signup Flow:
```
1. User fills signup form
   ↓
2. Frontend sends data to backend
   ↓
3. Backend creates Supabase Auth user
   ↓
4. Supabase sends verification email automatically
   ↓
5. User data stored in pending_signups table
   ↓
6. User clicks email link → Supabase verifies
   ↓
7. Webhook/check confirms verification
   ↓
8. Backend creates actual user account
   ↓
9. User can now login
```

### Benefits:
- ✅ **Free** - 50,000 monthly active users
- ✅ **Automatic email sending** - No need for SMTP setup
- ✅ **Secure** - Industry-standard JWT tokens
- ✅ **No password storage** - Supabase handles it
- ✅ **Built-in rate limiting** - Prevents spam
- ✅ **Email templates** - Customizable
- ✅ **Magic links** - Passwordless login option

---

## 🔧 Database Migration

Run this to create the pending_signups table:

```bash
cd Backend
python create_pending_signups_table.py
```

Or manually in MySQL:

```sql
CREATE TABLE pending_signups (
    id VARCHAR(36) PRIMARY KEY,
    supabase_user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    location VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    INDEX idx_supabase_user_id (supabase_user_id),
    INDEX idx_email (email),
    INDEX idx_expires_at (expires_at)
);

-- Add supabase_user_id to users table
ALTER TABLE users ADD COLUMN supabase_user_id VARCHAR(255);
ALTER TABLE users ADD INDEX idx_supabase_user_id (supabase_user_id);
```

---

## 🧪 Testing

### Test Signup:
1. Start backend: `python -m uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Go to signup page
4. Enter test email (use a real email you can access)
5. Check your email for verification link
6. Click link → Account created!

### Check Supabase Dashboard:
- **Authentication** → **Users** - See all registered users
- View email verification status
- Manually verify users if needed (for testing)

---

## 🔐 Security Notes

1. **Never commit .env file** - Already in .gitignore
2. **Use environment variables** - For production deployment
3. **Rotate keys regularly** - In Supabase dashboard
4. **Enable RLS** - Row Level Security (optional, for advanced use)
5. **Monitor usage** - Check Supabase dashboard for suspicious activity

---

## 🆘 Troubleshooting

### "Supabase client not initialized"
- Check `.env` file exists in `Backend/` folder
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set correctly
- Restart the backend server

### "Email not sending"
- Check Supabase dashboard → **Authentication** → **Email** is enabled
- Verify email provider settings
- Check spam folder
- Use Supabase's default email for testing

### "User already exists"
- Check Supabase dashboard → **Authentication** → **Users**
- Delete test user and try again
- Or use a different email

---

## 📚 Next Steps

1. **Customize email templates** - Make them match your brand
2. **Add social auth** - Google, Facebook, etc. (also free!)
3. **Implement magic links** - Passwordless login
4. **Add phone auth** - SMS verification (requires Twilio)
5. **Set up webhooks** - Auto-create accounts on verification

---

## 💡 Pro Tips

- **Development**: Use `+` in Gmail (e.g., `yourname+test1@gmail.com`) for multiple test accounts
- **Production**: Set up custom SMTP for better deliverability
- **Monitoring**: Enable Supabase email notifications for auth events
- **Backup**: Export user data regularly from Supabase dashboard

---

**Need help?** Check the [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
