from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from django.http import JsonResponse

from .forms import ContactForm
from .models import Contact
from apps.core.models import SiteSettings


def get_client_ip(request):
    """Safely extracts client IP address from HTTP headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


def is_rate_limited(ip_address, max_requests=3, duration_seconds=3600):
    """
    Checks whether the IP address has exceeded the request threshold.
    Uses cache and database check for safety.
    """
    cache_key = f"contact_rl_{ip_address}"
    current_count = cache.get(cache_key, 0)
    if current_count >= max_requests:
        return True

    # Secondary check against database
    one_hour_ago = timezone.now() - timedelta(seconds=duration_seconds)
    db_count = Contact.objects.filter(ip_address=ip_address, created_at__gte=one_hour_ago).count()
    if db_count >= max_requests:
        cache.set(cache_key, db_count, timeout=duration_seconds)
        return True

    return False


def increment_rate_limit(ip_address, duration_seconds=3600):
    cache_key = f"contact_rl_{ip_address}"
    current_count = cache.get(cache_key, 0)
    cache.set(cache_key, current_count + 1, timeout=duration_seconds)


def contact_view(request):
    """
    Handles displaying and submitting the contact form with rate limiting.
    """
    site_settings_obj = SiteSettings.objects.first()
    ip_address = get_client_ip(request)

    if request.method == 'POST':
        if is_rate_limited(ip_address):
            error_message = (
                "Siz juda ko'p murojaat yubordingiz. "
                "Iltimos, 1 soatdan so'ng qayta urinib ko'ring (Cheklov: soatiga 3 ta)."
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_message}, status=429)

            messages.error(request, error_message)
            form = ContactForm(request.POST)
            return render(request, 'contact.html', {
                'form': form,
                'site_settings': site_settings_obj,
            }, status=429)

        form = ContactForm(request.POST)
        if form.is_valid():
            contact_instance = form.save(commit=False)
            contact_instance.ip_address = ip_address
            contact_instance.save()

            increment_rate_limit(ip_address)

            success_message = "Murojaatingiz muvaffaqiyatli qabul qilindi! Tez orada siz bilan bog'lanamiz."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': success_message})

            messages.success(request, success_message)
            return redirect('contacts:contact')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = ContactForm()

    return render(request, 'contact.html', {
        'form': form,
        'site_settings': site_settings_obj,
    })
