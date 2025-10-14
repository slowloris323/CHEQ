import requests
class ConfirmationService:
    def retrieveCHEQ(self, resource_uri):
        #TODO: validate that the resource_uri is pointing to a trusted resource-server
        cheq_endpoint = resource_uri + "cheq"
        response = requests.get(cheq_endpoint)
        #TODO: authenticate to the resource server
        CHEQ = response.json()
        #TODO: validate CHEQ object signature
        return CHEQ