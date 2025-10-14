from django.views import generic
from django.urls import reverse
from .models import Resource, ResourceToConfirmationMapping, Result
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializers import ResourceSerializer, ResourceToConfirmationMappingSerializer
import io
from datetime import datetime
from .services import SignatureService

host = "http://127.0.0.1:8080"
class IndexView(generic.ListView):
    template_name = "resource_server/index.html"
    context_object_name = "resource_list"

    def get_queryset(self):
        """
        Return the object within a business process, ordered by sequence number
        """
        return Resource.objects.order_by("process_id")

class ResourceView(APIView):
    def get(self, request, process_id):
        if process_id:
            if type(process_id) is int:
                resources = Resource.objects.filter(process_id=process_id)
                serializer = ResourceSerializer(resources, many=True)
                return Response(serializer.data)
            else:
                return Response(self, 422)
        else:
            return Response(self, 500)

class ResourceCHEQView(APIView):
    def get(self, request, process_id):
        #TODO: this needs to be gated behind confirmation server auth
        if process_id:
            if type(process_id) is int:
                resources = Resource.objects.filter(process_id=process_id)
                serializer = ResourceSerializer(resources, many=True)
                resource_execution_uri = host + reverse("resource_server:resource", kwargs={"process_id":process_id}) + "execute"

                CHEQ = {
                    "version": 1.0,
                    "operation": resource_execution_uri,
                    "operation name": process_id,
                    "inputs" :{
                        "parameters" : serializer.data
                    },
                    "date": datetime.now()
                }
                signedCHEQ = SignatureService.sign(self, CHEQ)
                return Response(signedCHEQ, 200)
            else:
                return Response(self, 422)
        else:
            return Response(self, 500)

class ResourceExecView(APIView):
    # TODO: implement the execution thoughtfully, this is just a placeholder
    def get(self, request, process_id):
        if process_id:
            if type(process_id) is int:
                resources = Resource.objects.filter(process_id=process_id)
                serializer = ResourceSerializer(resources, many=True)
                return Response(serializer.data)
            else:
                return Response(self, 422)
        else:
            return Response(self, 500)


class ResultView(APIView):
    def get(self, request, process_id):
        if process_id:
            if type(process_id) is int:
                result = Result.objects.filter(process_id=process_id)
                serializer = ResourceSerializer(result, many=True)
                return Response(serializer.data)
            else:
                return Response(self, 422)
        else:
            return Response(self, 500)

class ProcessExecutionWithConfirmation(APIView):
    def post(self, request):
        # This is where the AI agent will ask for an action to be performed
        # Respond with 202, resource URI, and confirmation URI
        data = request.data
        if type(data) is not dict:
            return Response(status=415)
        if len(data.keys()) != 1:
            return Response(status=422)
        if "process_id" not in data.keys():
            return Response(status=422)
        if type(data["process_id"]) is not int:
            return Response(status=422)

        #return the resource uri and confirmation uri to the agent
        process_id = data["process_id"]


        resource_uri = host + reverse("resource_server:resource", kwargs=data)
        result_uri = host + reverse("resource_server:result", kwargs=data)

        confirmation_query = ResourceToConfirmationMapping.objects.filter(process_id=process_id)
        confirmation_serializer = ResourceToConfirmationMappingSerializer(confirmation_query, many=True)
        confirmation_uri = confirmation_serializer.data[0]["confirmation_uri"]

        response = {
            "resource_uri": resource_uri,
            "confirmation_uri": confirmation_uri,
            "result_uri": result_uri
        }
        return Response(response, status=202)

#TODO:
# implement API endpoint that provides public key for signature verification
# implement confirmation server auth
