from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import translation
from django.conf import settings

from .models import SiteSettings, Statistic, GalleryImage, SchoolHistory
from apps.news.models import News
from apps.teachers.models import Teacher
from apps.achievements.models import Achievement


def home_view(request):
    """
    Home page view. Loads site settings, statistics, featured teachers,
    latest news, achievements and gallery previews.
    If accessed on dedicated admin port (9000), redirect to dashboard.
    """
    if ':9000' in request.get_host():
        return redirect('dashboard_home')

    site_settings_obj = SiteSettings.objects.first()
    statistics = Statistic.objects.filter(is_active=True).order_by('order')
    featured_teachers = Teacher.objects.filter(is_active=True, is_featured=True).order_by('order')[:8]
    latest_news = News.objects.filter(status='published').order_by('-published_at', '-created_at')[:6]
    carousel_news = News.objects.filter(status='published').order_by('-is_featured', '-published_at')[:5]
    recent_achievements = Achievement.objects.filter(is_active=True).order_by('-date')[:4]
    gallery_preview = GalleryImage.objects.filter(is_active=True).order_by('order', '-created_at')[:6]

    # Best teacher — most experienced featured teacher
    best_teacher = Teacher.objects.filter(is_active=True, is_featured=True).order_by('-experience_years').first()

    # Best student — latest top achievement (place = 1st)
    best_student = Achievement.objects.filter(
        is_active=True, place__in=['1', '1-o\'rin', '1st', 'Birinchi']
    ).order_by('-date').first()
    # fallback: any latest achievement
    if not best_student:
        best_student = Achievement.objects.filter(is_active=True).order_by('-date').first()

    context = {
        'site_settings': site_settings_obj,
        'statistics': statistics,
        'featured_teachers': featured_teachers,
        'latest_news': latest_news,
        'carousel_news': carousel_news,
        'recent_achievements': recent_achievements,
        'gallery_preview': gallery_preview,
        'best_teacher': best_teacher,
        'best_student': best_student,
    }
    return render(request, 'home.html', context)



def about_view(request):
    """
    About page view. Displays school overview, history timeline, and statistics.
    """
    site_settings_obj = SiteSettings.objects.first()
    history_items = SchoolHistory.objects.all().order_by('order', 'year')
    statistics = Statistic.objects.filter(is_active=True).order_by('order')

    context = {
        'site_settings': site_settings_obj,
        'history_items': history_items,
        'statistics': statistics,
    }
    return render(request, 'about.html', context)


def gallery_view(request):
    """
    Gallery page view. Supports category filtering.
    """
    category = request.GET.get('category', 'all')
    images = GalleryImage.objects.filter(is_active=True)

    if category and category != 'all':
        images = images.filter(category=category)

    images = images.order_by('order', '-created_at')

    context = {
        'images': images,
        'current_category': category,
        'categories': GalleryImage.CATEGORY_CHOICES,
    }
    return render(request, 'gallery.html', context)


@require_http_methods(["GET", "POST"])
def set_language_view(request):
    """
    API endpoint and view to set the session language.
    Accepts language code via POST or GET 'language' parameter.
    """
    lang_code = request.POST.get('language') or request.GET.get('language')
    next_url = request.POST.get('next') or request.GET.get('next') or '/'

    valid_codes = [code for code, _ in settings.LANGUAGES]
    if lang_code and lang_code in valid_codes:
        request.session['django_language'] = lang_code
        translation.activate(lang_code)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            response = JsonResponse({'status': 'ok', 'language': lang_code})
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            return response

        response = redirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        return response

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'error', 'message': 'Invalid language code'}, status=400)

    return redirect(next_url)


def keep_alive_view(request):
    """
    Lightweight keep-alive and healthcheck endpoint.
    Used by automated ping robots to keep Render active 24/7.
    """
    return JsonResponse({'status': 'ok', 'service': '19-maktab', 'alive': True})


def custom_404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)
