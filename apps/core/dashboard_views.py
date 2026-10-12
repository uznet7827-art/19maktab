from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
import uuid

from apps.core.models import SiteSettings, Statistic, GalleryImage
from apps.news.models import News, NewsCategory
from apps.teachers.models import Teacher, Department
from apps.contacts.models import Contact
from apps.achievements.models import Achievement


def staff_required(view_func):
    """Decorator ensuring only logged in staff/admin can access."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='/dashboard/login/'
    )
    return actual_decorator(view_func)


def dashboard_login_view(request):
    """Simple, elegant Uzbek login page for school administrators."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')
        
    error_message = None
    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        user = authenticate(request, username=u, password=p)
        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next') or '/dashboard/'
            return redirect(next_url)
        else:
            error_message = "Login yoki parol noto'g'ri kiritildi. Iltimos qaytadan urinib ko'ring."

    return render(request, 'dashboard/login.html', {'error_message': error_message})


def dashboard_logout_view(request):
    """Logout and redirect to dashboard login."""
    logout(request)
    messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('dashboard_login')


@staff_required
def dashboard_home(request):
    """Admin Dashboard Overview."""
    site_settings_obj = SiteSettings.objects.first()
    
    total_teachers = Teacher.objects.count()
    total_news = News.objects.count()
    total_achievements = Achievement.objects.count()
    total_contacts = Contact.objects.count()
    total_gallery = GalleryImage.objects.count()
    new_contacts_count = Contact.objects.filter(status='new').count()
    
    recent_contacts = Contact.objects.order_by('-created_at')[:4]
    recent_news = News.objects.order_by('-created_at')[:4]
    
    context = {
        'site_settings': site_settings_obj,
        'total_teachers': total_teachers,
        'total_news': total_news,
        'total_achievements': total_achievements,
        'total_contacts': total_contacts,
        'total_gallery': total_gallery,
        'new_contacts_count': new_contacts_count,
        'recent_contacts': recent_contacts,
        'recent_news': recent_news,
        'active_menu': 'home',
    }
    return render(request, 'dashboard/home.html', context)


# -----------------------------------------------------------------------------
# 1. YANGILIKLAR BOSHQARUVI (NEWS)
# -----------------------------------------------------------------------------
@staff_required
def dashboard_news(request):
    if request.method == 'POST':
        news_id = request.POST.get('news_id')
        action = request.POST.get('action')
        news_item = get_object_or_404(News, id=news_id)
        
        if action == 'toggle_publish':
            news_item.status = 'draft' if news_item.status == 'published' else 'published'
            news_item.save()
            messages.success(request, f"'{news_item.title}' maqolasi holati o'zgartirildi.")
        elif action == 'delete':
            news_item.delete()
            messages.success(request, "Maqola o'chirildi.")
            
        return redirect('dashboard_news')

    news_items = News.objects.select_related('category').order_by('-created_at')
    context = {
        'news_items': news_items,
        'active_menu': 'news',
    }
    return render(request, 'dashboard/news.html', context)


@staff_required
def dashboard_news_add(request):
    """Simple form to add news with image."""
    categories = NewsCategory.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category')
        excerpt = request.POST.get('excerpt', '').strip()
        content = request.POST.get('content', '').strip()
        status = request.POST.get('status', 'published')
        cover_image = request.FILES.get('cover_image')
        
        if title:
            base_slug = slugify(title) or f"news-{uuid.uuid4().hex[:6]}"
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            category = NewsCategory.objects.filter(id=category_id).first() if category_id else None
            
            news = News.objects.create(
                title=title,
                slug=slug,
                category=category,
                excerpt=excerpt or title,
                content=content or excerpt or title,
                status=status,
                cover_image=cover_image,
                published_at=timezone.now() if status == 'published' else None
            )
            messages.success(request, f"'{news.title}' yangiligi muvaffaqiyatli qo'shildi!")
            return redirect('dashboard_news')
        else:
            messages.error(request, "Iltimos, yangilik sarlavhasini kiriting.")

    context = {
        'categories': categories,
        'active_menu': 'news',
    }
    return render(request, 'dashboard/news_add.html', context)


# -----------------------------------------------------------------------------
# 2. O'QITUVCHILAR BOSHQARUVI (TEACHERS)
# -----------------------------------------------------------------------------
@staff_required
def dashboard_teachers(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        action = request.POST.get('action')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        if action == 'toggle_active':
            teacher.is_active = not teacher.is_active
            teacher.save()
            messages.success(request, f"{teacher.full_name} holati o'zgartirildi.")
        elif action == 'delete':
            teacher.delete()
            messages.success(request, f"{teacher.full_name} o'chirildi.")
            
        return redirect('dashboard_teachers')

    teachers = Teacher.objects.select_related('department').order_by('order', 'full_name')
    context = {
        'teachers': teachers,
        'active_menu': 'teachers',
    }
    return render(request, 'dashboard/teachers.html', context)


@staff_required
def dashboard_teacher_add(request):
    """Simple form to add a new teacher."""
    departments = Department.objects.all()
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        subject = request.POST.get('subject', '').strip()
        position = request.POST.get('position', '').strip()
        department_id = request.POST.get('department')
        experience_years = int(request.POST.get('experience_years', 0) or 0)
        education = request.POST.get('education', '').strip()
        bio = request.POST.get('bio', '').strip()
        photo = request.FILES.get('photo')
        
        if full_name and subject:
            dept = Department.objects.filter(id=department_id).first() if department_id else None
            teacher = Teacher.objects.create(
                full_name=full_name,
                subject=subject,
                position=position or "O'qituvchi",
                department=dept,
                experience_years=experience_years,
                education=education,
                bio=bio,
                photo=photo,
                is_active=True
            )
            messages.success(request, f"{teacher.full_name} muvaffaqiyatli qo'shildi!")
            return redirect('dashboard_teachers')
        else:
            messages.error(request, "Ustoz ismi va fanini kiritish majburiy.")

    context = {
        'departments': departments,
        'active_menu': 'teachers',
    }
    return render(request, 'dashboard/teacher_add.html', context)


# -----------------------------------------------------------------------------
# 3. O'QUVCHILAR YUTUQLARI (ACHIEVEMENTS)
# -----------------------------------------------------------------------------
@staff_required
def dashboard_achievements(request):
    if request.method == 'POST':
        ach_id = request.POST.get('achievement_id')
        action = request.POST.get('action')
        ach = get_object_or_404(Achievement, id=ach_id)
        if action == 'delete':
            ach.delete()
            messages.success(request, "Yutuq muvaffaqiyatli o'chirildi.")
        return redirect('dashboard_achievements')

    achievements = Achievement.objects.order_by('-date')
    context = {
        'achievements': achievements,
        'active_menu': 'achievements',
    }
    return render(request, 'dashboard/achievements.html', context)


@staff_required
def dashboard_achievement_add(request):
    """Simple form to add student achievement."""
    if request.method == 'POST':
        student_name = request.POST.get('student_name', '').strip()
        grade = request.POST.get('grade', '').strip()
        achievement_type = request.POST.get('achievement_type', 'olympiad')
        title = request.POST.get('title', '').strip()
        place = request.POST.get('place', '').strip()
        description = request.POST.get('description', '').strip()
        photo = request.FILES.get('photo')
        
        if student_name and title:
            Achievement.objects.create(
                student_name=student_name,
                grade=grade,
                achievement_type=achievement_type,
                title=title,
                place=place or "1-o'rin",
                description=description,
                photo=photo,
                date=timezone.now().date(),
                is_active=True,
                parent_consent=True
            )
            messages.success(request, f"{student_name} yutug'i muvaffaqiyatli qo'shildi!")
            return redirect('dashboard_achievements')
        else:
            messages.error(request, "O'quvchi ismi va yutuq nomini kiritish majburiy.")

    context = {
        'active_menu': 'achievements',
        'type_choices': Achievement.TYPE_CHOICES,
    }
    return render(request, 'dashboard/achievement_add.html', context)


# -----------------------------------------------------------------------------
# 4. FOTOGALEREYA BOSHQARUVI (GALLERY)
# -----------------------------------------------------------------------------
@staff_required
def dashboard_gallery(request):
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        action = request.POST.get('action')
        img = get_object_or_404(GalleryImage, id=image_id)
        if action == 'delete':
            img.delete()
            messages.success(request, "Rasm galereyadan o'chirildi.")
        return redirect('dashboard_gallery')

    images = GalleryImage.objects.order_by('-created_at')
    context = {
        'images': images,
        'active_menu': 'gallery',
    }
    return render(request, 'dashboard/gallery.html', context)


@staff_required
def dashboard_gallery_add(request):
    """Simple form to upload photo into gallery."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'school')
        image = request.FILES.get('image')
        
        if image and title:
            GalleryImage.objects.create(
                title=title,
                category=category,
                image=image,
                is_active=True
            )
            messages.success(request, "Yangi rasm galereyaga muvaffaqiyatli yuklandi!")
            return redirect('dashboard_gallery')
        else:
            messages.error(request, "Rasm va uning nomini kiritish majburiy.")

    context = {
        'active_menu': 'gallery',
        'category_choices': GalleryImage.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/gallery_add.html', context)


# -----------------------------------------------------------------------------
# 5. MUROJAATLAR BOSHQARUVI (CONTACTS)
# -----------------------------------------------------------------------------
@staff_required
def dashboard_contacts(request):
    status_filter = request.GET.get('status')
    contacts = Contact.objects.all().order_by('-created_at')
    
    if status_filter:
        contacts = contacts.filter(status=status_filter)
        
    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        new_status = request.POST.get('new_status')
        admin_reply = request.POST.get('admin_reply', '').strip()
        action = request.POST.get('action')
        
        contact_item = get_object_or_404(Contact, id=contact_id)
        
        if action == 'delete':
            contact_item.delete()
            messages.success(request, "Murojaat o'chirildi.")
        elif new_status in dict(Contact.STATUS_CHOICES):
            contact_item.status = new_status
            if admin_reply:
                contact_item.admin_reply = admin_reply
            contact_item.save()
            messages.success(request, "Murojaat holati yangilandi.")
            
        return redirect('dashboard_contacts')

    context = {
        'contacts': contacts,
        'status_filter': status_filter,
        'active_menu': 'contacts',
    }
    return render(request, 'dashboard/contacts.html', context)


# -----------------------------------------------------------------------------
# 6. MAKTAB SOZLAMALARI (SETTINGS)
# -----------------------------------------------------------------------------
@staff_required
def dashboard_settings(request):
    site_settings_obj, _ = SiteSettings.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        site_settings_obj.school_name = request.POST.get('school_name', site_settings_obj.school_name)
        site_settings_obj.tagline = request.POST.get('tagline', site_settings_obj.tagline)
        site_settings_obj.phone = request.POST.get('phone', site_settings_obj.phone)
        site_settings_obj.email = request.POST.get('email', site_settings_obj.email)
        site_settings_obj.address = request.POST.get('address', site_settings_obj.address)
        site_settings_obj.working_hours = request.POST.get('working_hours', site_settings_obj.working_hours)
        site_settings_obj.director_name = request.POST.get('director_name', site_settings_obj.director_name)
        site_settings_obj.director_message = request.POST.get('director_message', site_settings_obj.director_message)
        site_settings_obj.telegram_url = request.POST.get('telegram_url', site_settings_obj.telegram_url)
        site_settings_obj.save()
        messages.success(request, "Maktab sozlamalari muvaffaqiyatli saqlandi!")
        return redirect('dashboard_settings')

    context = {
        'settings': site_settings_obj,
        'active_menu': 'settings',
    }
    return render(request, 'dashboard/settings.html', context)
