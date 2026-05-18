from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import  AirlineService
# Create your views here.

class SearchFights(APIView):
    def post(self, request):
        data = request.data
        print(f"DEBUG: Received params = {data}")
        airline_service = AirlineService()
        flights = airline_service.get_flights(data)
        return Response(flights)