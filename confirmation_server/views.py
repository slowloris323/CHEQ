from wsgiref.validate import validator

from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .services import ConfirmationService

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
            return Response(status=415)
        if len(data.keys()) != 1:
            return Response(status=422)
        if "resource_uri" not in data.keys():
            return Response(status=422)
        resource_uri_validator = URLValidator(schemes=['http', 'https'])
        try:
            resource_uri = data['resource_uri']
            resource_uri_validator(resource_uri)
        except ValidationError as e:
            print(f"Invalid resource URI: {e}")
            return Response(status=422)

        CHEQ = ConfirmationService.retrieveCHEQ(self, resource_uri)
        return Response(CHEQ, 200)

