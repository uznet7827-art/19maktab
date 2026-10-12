from .models import SiteSettings


def site_settings(request):
    """
    Context processor to make SiteSettings available in all templates.
    """
    settings_obj = SiteSettings.objects.first()
    return {
        'site_settings': settings_obj,
    }
