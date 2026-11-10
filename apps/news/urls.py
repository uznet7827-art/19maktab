from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list_view, name='list'),
    path('api/create-from-bot/', views.create_news_from_bot_api, name='create_from_bot'),
    path('<slug:slug>/', views.news_detail_view, name='detail'),
]
