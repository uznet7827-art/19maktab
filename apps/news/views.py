import os
import uuid
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.utils import timezone

from .models import News, NewsCategory, NewsImage


def news_list_view(request):
    """
    List view for news articles with search, category filtering, and pagination.
    """
    queryset = News.objects.filter(status='published').select_related('category')

    # Category filter
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(NewsCategory, slug=category_slug)
        queryset = queryset.filter(category=selected_category)

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(title_ru__icontains=query) |
            Q(title_en__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        )

    # Pagination
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = NewsCategory.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
    }
    return render(request, 'news/news_list.html', context)


def news_detail_view(request, slug):
    """
    Detail view for news articles. Increments views count safely.
    """
    news = get_object_or_404(
        News.objects.prefetch_related('images', 'videos', 'documents').select_related('category'),
        slug=slug,
        status='published'
    )

    # Increment view count
    News.objects.filter(pk=news.pk).update(views_count=F('views_count') + 1)
    news.refresh_from_db(fields=['views_count'])

    # Recent/related news
    related_news = News.objects.filter(
        status='published'
    ).exclude(pk=news.pk).order_by('-published_at')[:3]

    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'news/news_detail.html', context)


@require_GET
def news_carousel_api(request):
    """
    JSON API endpoint returning top featured / latest published news for interactive carousel.
    """
    news_items = News.objects.filter(status='published').order_by('-is_featured', '-published_at')[:5]

    data = []
    for item in news_items:
        data.append({
            'id': item.id,
            'title': item.localized_title,
            'slug': item.slug,
            'url': item.get_absolute_url(),
            'cover_image': item.cover_image.url if item.cover_image else None,
            'excerpt': item.localized_excerpt,
            'published_at': item.published_at.strftime('%Y-%m-%d %H:%M') if item.published_at else '',
            'category': {
                'name': item.category.localized_name if item.category else None,
                'color': item.category.color if item.category else '#4F46E5',
            } if item.category else None,
            'views_count': item.views_count,
        })

    return JsonResponse({'status': 'ok', 'count': len(data), 'results': data})


BOT_SECRET_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8864775756:AAECLlA465NwQR0E-93CYy07HPiuSs2B7Ko')


@csrf_exempt
@require_POST
def create_news_from_bot_api(request):
    """
    API endpoint for Telegram News Bot to publish news directly to the website.
    Secured by X-Bot-Token header.
    """
    token = request.headers.get('X-Bot-Token') or request.POST.get('bot_token')
    if not token or token != BOT_SECRET_TOKEN:
        return JsonResponse({'status': 'error', 'message': 'Ruxsat berilmadi (Noto\'g\'ri token)'}, status=403)

    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    excerpt = request.POST.get('excerpt', '').strip()
    category_name = request.POST.get('category', "Maktab yangiliklari").strip()

    if not title:
        return JsonResponse({'status': 'error', 'message': 'Sarlavha bo\'sh bo\'lishi mumkin emas'}, status=400)

    if not content:
        content = title

    if not excerpt:
        excerpt = content[:200] + ('...' if len(content) > 200 else '')

    category, _ = NewsCategory.objects.get_or_create(
        name=category_name,
        defaults={'slug': slugify(category_name) or 'yangiliklar', 'color': '#4F46E5'}
    )

    base_slug = slugify(title)
    if not base_slug:
        base_slug = f"news-{uuid.uuid4().hex[:8]}"
    slug = base_slug
    counter = 1
    while News.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    cover_image = request.FILES.get('cover_image')

    news_item = News.objects.create(
        title=title,
        slug=slug,
        category=category,
        excerpt=excerpt,
        content=content,
        cover_image=cover_image,
        status='published',
        published_at=timezone.now(),
        is_featured=True
    )

    gallery_files = request.FILES.getlist('gallery_images')
    for idx, gfile in enumerate(gallery_files, start=1):
        NewsImage.objects.create(
            news=news_item,
            image=gfile,
            order=idx
        )

    full_url = request.build_absolute_uri(news_item.get_absolute_url())

    return JsonResponse({
        'status': 'ok',
        'id': news_item.id,
        'title': news_item.title,
        'slug': news_item.slug,
        'url': full_url,
        'message': 'Yangilik muvaffaqiyatli e\'lon qilindi!'
    })
