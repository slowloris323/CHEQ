import os
import jwt

# BASE_DIR points to the project root where the .pem key files are stored
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SignatureService:
    def sign(self, CHEQ):
        try:
            # Changed from dotenv: reading rs_private_key.pem directly because dotenv cannot parse multiline PEM keys
            with open(os.path.join(BASE_DIR, 'rs_private_key.pem'), 'r') as f:
                signing_key = f.read()
            encoded_jwt = jwt.encode({"CHEQ": CHEQ}, signing_key, algorithm="RS256")
            return encoded_jwt
        except Exception as e:
            raise e

    def verify(self, CHEQ):
        try:
            # Changed from dotenv: reading cs_public_key.pem directly because dotenv cannot parse multiline PEM keys
            with open(os.path.join(BASE_DIR, 'cs_public_key.pem'), 'r') as f:
                verification_key = f.read()
            decoded_jwt = jwt.decode(CHEQ, verification_key, algorithms=["RS256"], verify_signature=True, require=["CHEQ"])
            return decoded_jwt
        except Exception as e:
            raise e