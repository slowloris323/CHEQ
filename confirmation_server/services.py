import requests
import jwt
import os
from dotenv import load_dotenv

class ConfirmationService:
    def retrieveCHEQ(self, resource_uri):
        try:
            #TODO: validate that the resource_uri is pointing to a trusted resource-server
            cheq_endpoint = resource_uri + "cheq"
            response = requests.get(cheq_endpoint)
            if response.status_code == 404:
                raise IndexError#getting a 500 here instead of 404
            #TODO: authenticate to the resource server
            CHEQ = response.text
            if CHEQ[-1] == '"':
                CHEQ = CHEQ[:-1]
            if CHEQ[0] == '"':
                CHEQ = CHEQ[1:]
            #TODO: pull the verification key from a location published by the resource server
            load_dotenv()
            verification_key = os.getenv("RS_PUBLIC_VERIFICATION_KEY")
            verified_CHEQ = jwt.decode(CHEQ, verification_key, algorithms="RS256", verify_signature=True, require=["CHEQ"])
        except Exception as e:
            raise e
        return verified_CHEQ

    def sign(self, CHEQ):
        try:
            load_dotenv()
            """
            Key generation:
            $ openssl genrsa -out private_key.pem 2048   
            $ openssl rsa -pubout -in private_key.pem -out public_key.pem   
            """
            signing_key = os.getenv('CS_PRIVATE_SIGNING_KEY')
            encoded_jwt = jwt.encode({"CHEQ": CHEQ}, signing_key, algorithm="RS256")
            return encoded_jwt
        except Exception as e:
            raise e

    def sendDecisionToRS(self, CHEQ, decision, resource_uri):
        signed_cheq = ConfirmationService.sign(self, CHEQ)
        response=requests.post(resource_uri,
                               data={"signed_CHEQ": signed_cheq},
                               params={"decision":decision})
        return response
