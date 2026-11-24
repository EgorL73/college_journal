from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Student, Grade, Group
from .forms import GradeForm

def home(request):
    return render(request, 'journal/home.html', {
        'students': Student.objects.count(),
        'groups': Group.objects.count(),
        'grades': Grade.objects.count(),
        'latest': Grade.objects.select_related('student__user', 'lesson__load__subject')[:5],
    })

def students(request):
    qs = Student.objects.select_related('user', 'group').order_by('user__last_name')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(user__last_name__icontains=q)
    return render(request, 'journal/students.html', {
        'page_obj': Paginator(qs, 20).get_page(request.GET.get('page')),
        'q': q,
    })

def student(request, pk):
    s = get_object_or_404(Student, pk=pk)
    return render(request, 'journal/student.html', {
        'student': s,
        'grades': s.grades.select_related('lesson__load__subject'),
    })

def grades(request):
    qs = Grade.objects.select_related('student__user', 'student__group', 'lesson__load__subject').order_by('-date')
    g = request.GET.get('group')
    if g:
        qs = qs.filter(lesson__load__group_id=g)
    return render(request, 'journal/grades.html', {
        'page_obj': Paginator(qs, 20).get_page(request.GET.get('page')),
        'groups': Group.objects.all(),
        'current_group': g,
    })

def grade_add(request):
    form = GradeForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Оценка добавлена!')
        return redirect('journal:grades')
    return render(request, 'journal/grade_form.html', {'form': form})

def about(request):
    return render(request, 'journal/about.html')

# --- API для fetch ---
from django.http import JsonResponse
from django.db.models import Q

def api_students(request):
    q = request.GET.get('q', '').strip()
    qs = Student.objects.select_related('user', 'group').all()
    if q:
        qs = qs.filter(Q(user__last_name__icontains=q) | Q(user__first_name__icontains=q))
    data = [{
        'id': s.pk, 
        'name': s.full_name, 
        'group': s.group.name, 
        'url': s.get_absolute_url
    } for s in qs[:20]]
    return JsonResponse({'students': data})