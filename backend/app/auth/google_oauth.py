from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Optional
from ..config.settings import settings


def verify_google_token(token: str) -> Optional[dict]:
    """Verify a Google ID token and return user info."""
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_client_id
        )
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'sub': idinfo.get('sub'),  # Google user ID
        }
    except ValueError:
        return None


def get_google_auth_url(state: Optional[str] = None) -> str:
    """Generate Google OAuth authorization URL."""
    from urllib.parse import urlencode
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        'client_id': settings.google_client_id,
        'redirect_uri': settings.google_redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    
    if state:
        params['state'] = state
    
    return f"{base_url}?{urlencode(params)}"

