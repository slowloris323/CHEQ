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
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key

        try:
            agent = AgentService()
            agent_response = agent.chat(user_message, session_id=session_id)

            return Response({
                "user_message": user_message,
                "agent_response": agent_response,
                "session_id": session_id
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class ClearMemoryView(APIView):
    """Clear conversation memory"""

    def post(self, request):

        if not not request.session.session_key:
            return Response(
                {"error": "No session_id provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        session_id = request.session.session_key
        try:
            agent = AgentService()
            agent.clear_memory(session_id=session_id)

            return Response({
                "message": f"Memory cleared"
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )