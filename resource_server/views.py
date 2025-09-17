from django.views import generic
from .models import Resource
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ResourceSerializer

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
        params = request.GET.get("process_id", None)
        if params:
            resources = Resource.objects.filter(params)
            serializer = ResourceSerializer(resources, many=True)
            return Response(serializer.data)
        else:
            return Response(self, 500)