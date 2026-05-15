import os
import jwt
import requests

# BASE_DIR points to the project root where the .pem key files are stored
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ConfirmationService:
    def retrieveCHEQ(self, resource_uri):
        try:
            # Added trailing slash to match Django's APPEND_SLASH setting
            cheq_endpoint = resource_uri + "cheq/"
            response = requests.get(cheq_endpoint)
            if response.status_code == 404:
                raise IndexError
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
        response = requests.post(resource_uri,
                                 data={"signed_CHEQ": signed_cheq},
                                 params={"decision": decision})
        return response
    def sendDecisionToRS(self, CHEQ, decision, resource_uri):
        signed_cheq = ConfirmationService.sign(self, CHEQ)
        response=requests.post(resource_uri,
                               data={"signed_CHEQ": signed_cheq},
                               params={"decision":decision})
        return response
