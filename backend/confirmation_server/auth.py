import os
import jwt
from jwt import PyJWKClient
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class Auth0User:
    def __init__(self, token_payload):
        self.payload = token_payload
        self.username = token_payload.get("sub")
        self.is_authenticated = True

    def __str__(self):
        return self.username

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

class Auth0JWTAuthentication(BaseAuthentication):
    _jwks_client = None

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if parts[0].lower() != "bearer":
            return None

        if len(parts) == 1:
            raise AuthenticationFailed("Invalid token header. No credentials provided.")
        elif len(parts) > 2:
            raise AuthenticationFailed("Invalid token header. Token string should not contain spaces.")

        token = parts[1]

        auth0_domain = os.getenv("AUTH0_DOMAIN") or getattr(settings, "AUTH0_DOMAIN", "")
        auth0_audience = os.getenv("AUTH0_AUDIENCE") or getattr(settings, "AUTH0_AUDIENCE", "")

        if not auth0_domain or not auth0_audience:
            raise AuthenticationFailed("Auth0 domain or audience is not configured in environment variables.")

        if Auth0JWTAuthentication._jwks_client is None:
            jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
            ssl_context = None
            if getattr(settings, "DEBUG", False):
                import ssl
                ssl_context = ssl._create_unverified_context()
            Auth0JWTAuthentication._jwks_client = PyJWKClient(jwks_url, ssl_context=ssl_context)


        try:
            # Retrieve the signing key using the kid from the JWT token
            signing_key = Auth0JWTAuthentication._jwks_client.get_signing_key_from_jwt(token)
            
            # Decode the token and verify signature, audience, issuer, and expiration
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=auth0_audience,
                issuer=f"https://{auth0_domain}/"
            )
            
            user = Auth0User(payload)
            return (user, token)

        except jwt.ExpiredSignatureError as e:
            print(f"Auth0 JWT Verification failed: Token expired ({e})")
            raise AuthenticationFailed("Token has expired.")
        except jwt.InvalidSignatureError as e:
            print(f"Auth0 JWT Verification failed: Invalid signature ({e})")
            raise AuthenticationFailed("Token signature is invalid.")
        except jwt.DecodeError as e:
            print(f"Auth0 JWT Verification failed: Decode error ({e})")
            raise AuthenticationFailed("Token decoding failed.")
        except Exception as e:
            print(f"Auth0 JWT Verification failed: Unexpected error ({e})")
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")

