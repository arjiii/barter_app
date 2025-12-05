# Email Configuration Guide

To enable OTP email verification, you need to ensure your Supabase project is configured correctly.
We have switched to using **Supabase Auth** to send verification emails, so you do **NOT** need to configure Gmail SMTP anymore.

### Supabase Email Configuration
1. Go to your Supabase Project Dashboard
2. Navigate to **Authentication** -> **Providers** -> **Email**
3. Ensure **Enable Email Provider** is ON
4. Ensure **Confirm Email** is ON (or OFF if you want to skip verification, but our app expects it)
5. **IMPORTANT:** For the OTP code to work in our app, you should ensure the email template includes the code.
   - Go to **Authentication** -> **Email Templates** -> **Magic Link**
   - Ensure the body contains `{{ .Token }}` to show the 6-digit code.
   - Example: `<p>Your verification code is: <strong>{{ .Token }}</strong></p>`

### Environment Variables
Ensure `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set in your `Backend/.env` file.


### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification

### Step 2: Create an App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "Bayanihan Exchange"
4. Copy the generated 16-character password

### Step 3: Update .env File

Add these lines to your `Backend/.env` file:

```env
# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=Bayanihan Exchange
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True
FRONTEND_URL=http://localhost:5173
```

Replace:
- `your-email@gmail.com` with your actual Gmail address
- `your-16-char-app-password` with the App Password from Step 2

### Step 4: Restart the Backend Server

After updating the .env file, restart your backend server for changes to take effect.

## Alternative: Admin Verification

If you don't want to set up email, users can select "Verify via Admin Request (Manual Approval)" during signup. The admin can then approve them from the admin panel at `/admin/users`.

### To Approve Users:
1. Go to http://localhost:5173/admin/users
2. Find pending users with "Pending Approval" status
3. Click "Approve" to activate their account

## Troubleshooting

### "Failed to send verification email" Error
- Make sure you're using an App Password, not your regular Gmail password
- Check that 2-Factor Authentication is enabled on your Google account
- Verify all email settings in .env are correct
- Check backend console for detailed error messages

### Gmail blocks the email
- Make sure "Less secure app access" is OFF (use App Passwords instead)
- Check Gmail's "Blocked Account" settings
- Try sending a test email from Gmail to verify your account is working
