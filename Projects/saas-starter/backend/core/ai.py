import openai
from django.conf import settings

# Set API key if available
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

def ask_ai(message):
    """Ask AI a question. Returns a response or error message if OpenAI is not configured."""
    if not settings.OPENAI_API_KEY:
        return "AI features are not configured. Please set OPENAI_API_KEY in your environment variables."
    
    try:
        r = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":message}]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"
