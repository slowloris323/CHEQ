from dotenv import load_dotenv
import os
import jwt

class SignatureService:
    def sign(self, CHEQ):
        try:
            load_dotenv()
            """
            Key generation:
            $ openssl genrsa -out private_key.pem 2048   
            $ openssl rsa -pubout -in private_key.pem -out public_key.pem   
            """
            signing_key = os.getenv('RS_PRIVATE_SIGNING_KEY')
            encoded_jwt = jwt.encode({"CHEQ": CHEQ}, signing_key, algorithm="RS256")
            return encoded_jwt
        except Exception as e:
            raise e

    def verify(self, CHEQ):
        try:
            load_dotenv()
            verification_key = os.getenv('CS_PUBLIC_VERIFICATION_KEY')
            decoded_jwt = jwt.decode(CHEQ, verification_key, algorithms="RS256", verify_signature=True, require=["CHEQ"])
            return decoded_jwt
        except Exception as e:
            raise e