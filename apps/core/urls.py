from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('api/set-language/', views.set_language_view, name='set_language'),
]
