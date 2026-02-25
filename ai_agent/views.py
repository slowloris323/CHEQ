from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import AgentService

class ChatView(APIView):
    def post(self, request):
        user_message = request.data.get('message')

        if not user_message:
            return Response(
                {"error": "No message provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            agent = AgentService()
            agent_response = agent.chat(user_message)

            return Response({
                "user_message": user_message,
                "agent_response": agent_response
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )