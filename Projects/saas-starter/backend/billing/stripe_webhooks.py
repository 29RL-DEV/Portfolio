import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import WebhookEvent
from users.models import Profile


stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)

    event_id = event["id"]
    event_type = event["type"]

    # Idempotency
    webhook_event, created = WebhookEvent.objects.get_or_create(
        event_id=event_id,
        defaults={
            "event_type": event_type,
            "event_data": event
        }
    )

    if not created and webhook_event.processed:
        return HttpResponse(status=200)

    try:
        handle_event(event)
        webhook_event.mark_processed()
    except Exception as e:
        webhook_event.mark_processed(str(e))
        return HttpResponse(status=500)

    return HttpResponse(status=200)
