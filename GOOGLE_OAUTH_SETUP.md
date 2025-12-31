# Google OAuth Setup Guide

## ✅ Implementation Complete

Google OAuth authentication has been added to your application! Users can now sign in with their Google account.

## 🔧 Setup Instructions

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API** (or **Google Identity Services**)
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Choose **Web application**
6. Add authorized JavaScript origins:
   - `http://localhost:5173` (development)
   - Your production domain (e.g., `https://yourdomain.com`)
7. Add authorized redirect URIs:
   - `http://localhost:5173` (development)
   - Your production domain
8. Copy the **Client ID** and **Client Secret**

### 2. Backend Configuration

Add to your `backend/app/.env` file:

```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

**Note:** The redirect URI in the backend config is optional for this implementation since we're using the frontend flow.

### 3. Frontend Configuration

Create or update `frontend/.env`:

```env
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

**Important:** The frontend needs the Client ID to initialize the Google Sign-In button.

### 4. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend (no additional packages needed - using Google's CDN)
```

## 🎯 How It Works

1. **User clicks "Sign in with Google"** on the login page
2. **Google Identity Services** handles the OAuth flow
3. **Frontend receives** a Google ID token
4. **Frontend sends token** to `/auth/google/callback`
5. **Backend verifies** the token with Google
6. **Backend creates/updates user** in database
7. **Backend returns JWT tokens** (access + refresh)
8. **User is logged in** with your app's authentication

## 📝 API Endpoints

### `GET /auth/google/login`
Returns the Google OAuth URL (optional - not used in current implementation)

### `POST /auth/google/callback`
Accepts Google ID token and returns JWT tokens

**Request:**
```json
{
  "token": "google-id-token-here"
}
```

**Response:**
```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer"
}
```

## 🔒 Security Notes

1. **Token Verification**: Backend verifies Google tokens server-side
2. **User Creation**: New users are automatically created if they don't exist
3. **Email Matching**: Users are matched by email address
4. **Password**: OAuth users have an empty password hash (they can't use email/password login unless they set a password)

## 🐛 Troubleshooting

### Google Sign-In button doesn't appear
- Check that `VITE_GOOGLE_CLIENT_ID` is set in frontend `.env`
- Check browser console for errors
- Verify Google script is loading (check Network tab)

### "Invalid Google token" error
- Verify `GOOGLE_CLIENT_ID` matches in both frontend and backend
- Check that the token hasn't expired
- Ensure Google Identity Services is properly initialized

### CORS errors
- Make sure your frontend URL is in Google's authorized JavaScript origins
- Check backend CORS settings in `config/settings.py`

## 🚀 Testing

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to login page
4. Click "Sign in with Google"
5. Complete Google authentication
6. You should be redirected to the home page, logged in!

## 📚 Additional Resources

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)

