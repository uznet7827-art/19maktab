from django.shortcuts import render
from .models import Achievement


def achievement_list_view(request):
    """
    List view for student achievements.
    """
    type_filter = request.GET.get('type')
    queryset = Achievement.objects.filter(is_active=True)

    if type_filter and type_filter in dict(Achievement.TYPE_CHOICES):
        queryset = queryset.filter(achievement_type=type_filter)

    achievements = queryset.order_by('-date', '-created_at')

    context = {
        'achievements': achievements,
        'types': Achievement.TYPE_CHOICES,
        'selected_type': type_filter,
    }
    return render(request, 'home.html', context)
