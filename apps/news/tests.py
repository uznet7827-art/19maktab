from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import News, NewsCategory


class NewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = NewsCategory.objects.create(
            name="Ta'lim",
            name_ru="Образование",
            name_en="Education",
            slug="talim"
        )
        self.published_news = News.objects.create(
            title="19-maktabda yangi o'quv yili boshlandi",
            slug="yangi-oquv-yili-boshlandi",
            category=self.category,
            excerpt="Yangi o'quv yili tantanali ravishda ochildi.",
            content="Barcha o'quvchilar va ustozlar uchun yangi o'quv yili boshlandi.",
            status="published",
            published_at=timezone.now(),
            is_featured=True
        )
        self.draft_news = News.objects.create(
            title="Qoralama yangilik",
            slug="qoralama-yangilik",
            category=self.category,
            excerpt="Bu hali e'lon qilinmagan.",
            content="Matn qoralama holatida.",
            status="draft"
        )

    def test_news_list_view_status_code(self):
        response = self.client.get(reverse('news:list'))
        self.assertEqual(response.status_code, 200)

    def test_news_list_shows_published_not_draft(self):
        response = self.client.get(reverse('news:list'))
        # Django HTML-escapes apostrophes, so check the slug link or HTML-escaped form
        self.assertContains(response, self.published_news.slug)  # slug is always safe
        self.assertNotContains(response, self.draft_news.slug)


    def test_news_detail_view_and_view_count(self):
        initial_views = self.published_news.views_count
        response = self.client.get(reverse('news:detail', kwargs={'slug': self.published_news.slug}))
        self.assertEqual(response.status_code, 200)
        self.published_news.refresh_from_db()
        self.assertEqual(self.published_news.views_count, initial_views + 1)

    def test_carousel_api_returns_json(self):
        response = self.client.get(reverse('news_carousel_api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertEqual(data.get('count'), 1)
        self.assertEqual(data['results'][0]['title'], self.published_news.title)
