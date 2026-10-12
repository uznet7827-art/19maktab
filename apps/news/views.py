from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import News, NewsCategory


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
