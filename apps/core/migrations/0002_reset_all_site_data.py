from django.db import migrations


def wipe_all_data(apps, schema_editor):
    News = apps.get_model('news', 'News')
    NewsCategory = apps.get_model('news', 'NewsCategory')
    NewsImage = apps.get_model('news', 'NewsImage')
    NewsVideo = apps.get_model('news', 'NewsVideo')
    NewsDocument = apps.get_model('news', 'NewsDocument')
    Teacher = apps.get_model('teachers', 'Teacher')
    Department = apps.get_model('teachers', 'Department')
    Achievement = apps.get_model('achievements', 'Achievement')
    GalleryImage = apps.get_model('core', 'GalleryImage')
    SchoolHistory = apps.get_model('core', 'SchoolHistory')
    Statistic = apps.get_model('core', 'Statistic')
    Contact = apps.get_model('contacts', 'Contact')
    SiteSettings = apps.get_model('core', 'SiteSettings')

    NewsImage.objects.all().delete()
    NewsVideo.objects.all().delete()
    NewsDocument.objects.all().delete()
    News.objects.all().delete()
    NewsCategory.objects.all().delete()
    Teacher.objects.all().delete()
    Department.objects.all().delete()
    Achievement.objects.all().delete()
    GalleryImage.objects.all().delete()
    SchoolHistory.objects.all().delete()
    Statistic.objects.all().delete()
    Contact.objects.all().delete()

    site = SiteSettings.objects.first()
    if site:
        site.about_text = ""
        site.about_text_ru = ""
        site.about_text_en = ""
        site.director_name = ""
        site.director_message = ""
        site.hero_image = None
        site.director_photo = None
        site.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('news', '0001_initial'),
        ('teachers', '0001_initial'),
        ('achievements', '0001_initial'),
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(wipe_all_data, migrations.RunPython.noop),
    ]
