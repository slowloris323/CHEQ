import os
import time
import jwt
import requests
from django.conf import settings

# BASE_DIR points to the project root where the .pem key files are stored
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_token_cache = {
    "access_token": None,
    "expires_at": 0
}

def get_access_token():
    global _token_cache
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 300:
        return _token_cache["access_token"]

    domain = getattr(settings, 'AUTH0_DOMAIN', None)
    client_id = getattr(settings, 'AUTH0_CLIENT_ID', None)
    client_secret = getattr(settings, 'AUTH0_CLIENT_SECRET', None)
    audience = getattr(settings, 'AUTH0_AUDIENCE', None)

    if not all([domain, client_id, client_secret, audience]):
        raise ValueError("Missing Auth0 configurations in settings/environment variables.")

    url = f"https://{domain}/oauth/token"
    headers = {"content-type": "application/json"}
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    access_token = data["access_token"]
    expires_in = data.get("expires_in", 86400)

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + expires_in

    return access_token

class ConfirmationService:
    def retrieveCHEQ(self, resource_uri):
        try:
            # Added trailing slash to match Django's APPEND_SLASH setting
            cheq_endpoint = resource_uri + "cheq/"
            headers = {
                "Authorization": f"Bearer {get_access_token()}"
            }
            response = requests.get(cheq_endpoint, headers=headers)
            if response.status_code == 404:
                raise IndexError
            response.raise_for_status()
            CHEQ = response.text.strip('"')
            # Changed from dotenv: reading rs_public_key.pem directly because dotenv cannot parse multiline PEM keys
            with open(os.path.join(BASE_DIR, 'rs_public_key.pem'), 'r') as f:
                verification_key = f.read()
            verified_CHEQ = jwt.decode(CHEQ, verification_key, algorithms=["RS256"], verify_signature=True, require=["CHEQ"])
        except Exception as e:
            raise e
        return verified_CHEQ

    def sign(self, CHEQ):
        try:
            # Changed from dotenv: reading cs_private_key.pem directly because dotenv cannot parse multiline PEM keys
            with open(os.path.join(BASE_DIR, 'cs_private_key.pem'), 'r') as f:
                signing_key = f.read()
            encoded_jwt = jwt.encode({"CHEQ": CHEQ}, signing_key, algorithm="RS256")
            return encoded_jwt
        except Exception as e:
            raise e

    def sendDecisionToRS(self, CHEQ, decision, resource_uri):
        signed_cheq = ConfirmationService.sign(self, CHEQ)
        headers = {
            "Authorization": f"Bearer {get_access_token()}"
        }
        response = requests.post(resource_uri,
                                 data={"signed_CHEQ": signed_cheq},
                                 params={"decision": decision},
                                 headers=headers)
        return response
