"""
URL configuration for maktab19 project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import home_view, about_view, gallery_view, presentation_view, set_language_view, custom_404_view, custom_500_view
from apps.core import dashboard_views
from apps.news.views import news_carousel_api

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core & Pages
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('gallery/', gallery_view, name='gallery'),
    path('presentation/', presentation_view, name='presentation'),
    path('slaydlar/', presentation_view, name='slaydlar'),
    path('contact/', include('apps.contacts.urls')),

    # Apps
    path('news/', include('apps.news.urls')),
    path('teachers/', include('apps.teachers.urls')),
    path('achievements/', include('apps.achievements.urls')),

    # APIs
    path('api/news/carousel/', news_carousel_api, name='news_carousel_api'),
    path('api/set-language/', set_language_view, name='set_language'),

    # Custom Admin Dashboard (Super simple Uzbek admin panel)
    path('dashboard/', include([
        path('login/', dashboard_views.dashboard_login_view, name='dashboard_login'),
        path('logout/', dashboard_views.dashboard_logout_view, name='dashboard_logout'),
        path('', dashboard_views.dashboard_home, name='dashboard_home'),
        path('contacts/', dashboard_views.dashboard_contacts, name='dashboard_contacts'),
        path('news/', dashboard_views.dashboard_news, name='dashboard_news'),
        path('news/add/', dashboard_views.dashboard_news_add, name='dashboard_news_add'),
        path('teachers/', dashboard_views.dashboard_teachers, name='dashboard_teachers'),
        path('teachers/add/', dashboard_views.dashboard_teacher_add, name='dashboard_teacher_add'),
        path('achievements/', dashboard_views.dashboard_achievements, name='dashboard_achievements'),
        path('achievements/add/', dashboard_views.dashboard_achievement_add, name='dashboard_achievement_add'),
        path('gallery/', dashboard_views.dashboard_gallery, name='dashboard_gallery'),
        path('gallery/add/', dashboard_views.dashboard_gallery_add, name='dashboard_gallery_add'),
        path('settings/', dashboard_views.dashboard_settings, name='dashboard_settings'),
    ])),
]

# Static & Media handling in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom error handlers
handler404 = custom_404_view
handler500 = custom_500_view

# Admin Site Header & Title customizations
admin.site.site_header = "19-maktab ma'muriyat paneli"
admin.site.site_title = "19-maktab boshqaruvi"
admin.site.index_title = "Maktab boshqaruv tizimiga xush kelibsiz"
