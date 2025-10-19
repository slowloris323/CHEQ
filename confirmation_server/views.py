from wsgiref.validate import validator

from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.urls import reverse


from .serializers import ResourceUriCheqMappingSerializer
from .services import ConfirmationService
from enum import Enum
from .models import ResourceUriCheqMapping

valid_decisions = ["ACCEPT", "REJECT"]
host = "http://127.0.0.1:8000"

class IndexView(generic.ListView):
    template_name = "confirmation_server/index.html"
    context_object_name = "confirmation_server_landing"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return True

class TriggerView(APIView):
    template_name = "confirmation_server/request_confirmation.html"

    def post(self, request):
        #TODO: implement user auth
        data = request.data
        #first need to validate and extract the resource URI
        if type(data) is not dict:
            return Response(415)
        if len(data.keys()) != 1:
            return Response(422)
        if "resource_uri" not in data.keys():
            return Response(422)
        resource_uri_validator = URLValidator(schemes=['http', 'https'])
        try:
            resource_uri = data['resource_uri']
            resource_uri_validator(resource_uri)
        except ValidationError as e:
            print(f"Invalid resource URI: {e}")
            return Response(422)

        try:
            response = ConfirmationService.retrieveCHEQ(self, resource_uri)
            #write to the DB resource_uri <> CHEQ mapping
            if not ResourceUriCheqMapping.objects.filter(resource_uri=resource_uri).exists():
                mapping = ResourceUriCheqMapping(
                    resource_uri= resource_uri,
                    CHEQ= response
                )
                mapping.save()

            perform_confirmation_uri = host + reverse("confirmation_server:perform")
            response["perform_confirmation_uri"] = perform_confirmation_uri
            return Response(response, 200)
        except Exception as e:
            return Response(500)

class PerformView(APIView):
    def post(self, request):
        data = request.data
        #Input validation
        #{"resource_uri": "http://127.0.0.1:8000/resource_server/resource/1/", "decision": "accept"}
        if type(data) is not dict:
            return Response(415)
        if len(data.keys()) != 2:
            return Response(422)
        if ("resource_uri" not in data.keys()) and ("decision" not in data.keys):
            return Response("Request boy must contain resource_uri and decision clauses", 422)

        resource_uri_validator = URLValidator(schemes=['http', 'https'])
        try:
            resource_uri = data['resource_uri']
            resource_uri_validator(resource_uri)
        except ValidationError as e:
            print(f"Invalid resource URI: {e}")
            return Response("Invalid resource URI", 422)

        if data["decision"] not in valid_decisions:
            print(f"Invalid decision")
            return Response("Invalid decision", 422)
        else:
            decision = data["decision"]

        #get cheq object from DB, and send to RS along with decision
        try:
            CHEQ_query = ResourceUriCheqMapping.objects.filter(resource_uri=resource_uri)
            CHEQ_serializer = ResourceUriCheqMappingSerializer(CHEQ_query, many=True)

            if CHEQ_serializer:
                CHEQ = CHEQ_serializer.data[0]['CHEQ']['CHEQ']
                response = ConfirmationService.sendDecisionToRS(self, CHEQ, decision, resource_uri)
                if response.status_code == 200:
                    return Response("Decision sent", 200)
                else:
                    return Response(response, 400)
            else:
                return Response("No CHEQ object registered for this resource URI", 400)
        except Exception as e:
            return Response("No CHEQ object registered for this resource URI", 400)






