from django.urls import path
from .views import ChatView, ClearMemoryView, ChatsView

app_name = "ai_agent"
urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("clear_memory/", ClearMemoryView.as_view(), name="clear_memory"),
    path("chats/", ChatsView.as_view(), name="chats"),
]