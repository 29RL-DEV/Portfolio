from django.urls import path
from .views_ai import chat

urlpatterns = [
    path("api/ai/chat/", chat, name="ai_chat"),
]
