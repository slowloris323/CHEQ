from django.shortcuts import render
from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Trigger
from .serializers import TriggerSerializer

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
    def get(self, request):
        triggers = Trigger.objects.all()
        serializer = TriggerSerializer(triggers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TriggerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)