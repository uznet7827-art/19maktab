from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Teacher, Department


def teacher_list_view(request):
    """
    List view for teachers with department filtering and search.
    """
    queryset = Teacher.objects.filter(is_active=True).select_related('department')

    department_id = request.GET.get('department')
    selected_department = None
    if department_id:
        selected_department = get_object_or_404(Department, id=department_id)
        queryset = queryset.filter(department=selected_department)

    query = request.GET.get('q', '').strip()
    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query) |
            Q(subject__icontains=query) |
            Q(position__icontains=query) |
            Q(education__icontains=query)
        )

    departments = Department.objects.all()

    context = {
        'teachers': queryset.order_by('order', 'full_name'),
        'departments': departments,
        'selected_department': selected_department,
        'query': query,
    }
    return render(request, 'teachers/teacher_list.html', context)


def teacher_detail_view(request, pk):
    """
    Detail view for teacher profile.
    """
    teacher = get_object_or_404(Teacher.objects.select_related('department'), pk=pk, is_active=True)

    colleagues = []
    if teacher.department:
        colleagues = Teacher.objects.filter(
            department=teacher.department,
            is_active=True
        ).exclude(pk=teacher.pk)[:4]

    context = {
        'teacher': teacher,
        'colleagues': colleagues,
    }
    return render(request, 'teachers/teacher_detail.html', context)
