# Email Authentication Setup Guide

## Overview
The forgot password and email verification features have been implemented. This guide explains how to configure email sending.

## Features Implemented

### Backend
1. **Password Reset Flow**
   - `/auth/forgot-password` - Request password reset (sends email)
   - `/auth/reset-password` - Reset password using token
   - Tokens expire after 1 hour

2. **Email Verification Flow**
   - `/auth/verify-email` - Verify email using token
   - `/auth/resend-verification` - Resend verification email
   - Verification tokens expire after 24 hours
   - Signup automatically sends verification email

### Frontend
1. **Forgot Password UI**
   - Modal on sign-in page
   - Reset password page at `/reset-password?token=...`

2. **Email Verification UI**
   - Automatic verification page at `/verify-email?token=...`
   - Shows success/error states

## Email Configuration

### Option 1: Gmail (Recommended for Development)

1. **Enable App Password in Gmail:**
   - Go to your Google Account settings
   - Security → 2-Step Verification (enable if not already)
   - App passwords → Generate app password
   - Copy the 16-character password

2. **Set Environment Variables in Railway:**
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   MAIL_FROM=your-email@gmail.com
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_FROM_NAME=Bayanihan Exchange
   FRONTEND_URL=https://barterappv3.vercel.app
   ```

### Option 2: SendGrid (Recommended for Production)

1. **Create SendGrid Account:**
   - Sign up at https://sendgrid.com
   - Create an API key

2. **Set Environment Variables:**
   ```
   MAIL_USERNAME=apikey
   MAIL_PASSWORD=your-sendgrid-api-key
   MAIL_FROM=noreply@yourdomain.com
   MAIL_SERVER=smtp.sendgrid.net
   MAIL_PORT=587
   MAIL_FROM_NAME=Bayanihan Exchange
   FRONTEND_URL=https://barterappv3.vercel.app
   ```

### Option 3: Other SMTP Providers

For other providers (Mailgun, AWS SES, etc.), update the environment variables accordingly:
- `MAIL_SERVER` - SMTP server address
- `MAIL_PORT` - Usually 587 (TLS) or 465 (SSL)
- `MAIL_USERNAME` - Your SMTP username
- `MAIL_PASSWORD` - Your SMTP password
- `MAIL_STARTTLS` - Set to `true` for port 587
- `MAIL_SSL_TLS` - Set to `true` for port 465

## Railway Configuration Steps

1. **Go to Railway Dashboard:**
   - Select your `barter_app` service
   - Go to "Variables" tab

2. **Add Email Environment Variables:**
   - Click "New Variable"
   - Add each variable from the list above
   - Make sure `FRONTEND_URL` matches your Vercel deployment URL

3. **Redeploy:**
   - After adding variables, Railway will automatically redeploy
   - Or manually trigger a redeploy

## Testing

### Test Password Reset:
1. Go to sign-in page
2. Click "Forgot Password?"
3. Enter your email
4. Check your email for reset link
5. Click link and reset password

### Test Email Verification:
1. Sign up with a new account
2. Check your email for verification link
3. Click link to verify email

## Troubleshooting

### Emails Not Sending:
1. Check Railway logs for email errors
2. Verify environment variables are set correctly
3. For Gmail: Make sure app password is correct (not your regular password)
4. Check spam folder

### Token Expired:
- Password reset tokens expire after 1 hour
- Email verification tokens expire after 24 hours
- Request a new token if expired

### Frontend URL Issues:
- Make sure `FRONTEND_URL` in Railway matches your Vercel URL exactly
- Include `https://` in the URL
- No trailing slash

## Security Notes

1. **Never commit email credentials to Git**
2. **Use environment variables only**
3. **For production, use a dedicated email service (SendGrid, AWS SES)**
4. **Gmail app passwords are fine for development/testing**

## Database Schema

The following fields were added to the `users` table:
- `email_verification_token` - Token for email verification
- `password_reset_token` - Token for password reset
- `password_reset_expires` - Expiration time for reset token

These fields are already in your database schema and don't require migration.

