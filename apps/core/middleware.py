from django.utils import translation
from django.conf import settings


class SessionLanguageMiddleware:
    """
    Middleware that activates language based on session or cookie.
    Allows dynamic language switching across the site.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.session.get('django_language')
        if not language:
            language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if not language or language not in [code for code, _ in settings.LANGUAGES]:
            language = settings.LANGUAGE_CODE

        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
