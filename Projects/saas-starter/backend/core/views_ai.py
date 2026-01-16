from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ai import ask_ai

@api_view(["POST"])
def chat(request):
    msg = request.data.get("message")
    reply = ask_ai(msg)
    return Response({"reply": reply})
