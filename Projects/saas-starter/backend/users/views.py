from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from django.core.mail import send_mail
from django.conf import settings


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def signup(request):
    """User registration/signup view"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Cont creat cu succes! Acum poți să te loghezi.")
            login(request, user)

            if settings.EMAIL_HOST_USER:
                try:
                    send_mail(
                        "Bun venit!",
                        f"Bun venit, {user.username}! Contul tău a fost creat cu succes.",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            return redirect("/")
        else:
            messages.error(
                request, "Eroare la crearea contului. Te rugăm să verifici datele."
            )
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


@ratelimit(key="ip", rate="10/h", method="POST", block=True)
def contact_form(request):
    """Contact form handler"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        # Validation
        if not all([name, email, subject, message_text]):
            messages.error(request, "Toate câmpurile sunt necesare.")
            return render(request, "contact.html")

        if len(message_text) < 10:
            messages.error(request, "Mesajul trebuie să aibă cel puțin 10 caractere.")
            return render(request, "contact.html")

        # Send email to admin
        admin_email = settings.DEFAULT_FROM_EMAIL or "admin@example.com"
        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=f"From: {name} ({email})\n\nMessage:\n{message_text}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )

            # Send confirmation email to user
            if settings.EMAIL_HOST_USER:
                try:
                    send_mail(
                        subject="Mesajul tău a fost primit",
                        message=f"Bun venit, {name}!\n\nAm primit mesajul tău și te vom contacta în curând.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            messages.success(
                request,
                "Mesajul tău a fost trimis cu succes! Te vom contacta în curând.",
            )
            return redirect("/")

        except Exception as e:
            messages.error(request, f"Eroare la trimitere: {str(e)}")
            return render(request, "contact.html")

    return render(request, "contact.html")
