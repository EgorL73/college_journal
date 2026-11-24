from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.home, name='home'),
    path('students/', views.students, name='students'),
    path('students/<int:pk>/', views.student, name='student'),
    path('grades/', views.grades, name='grades'),
    path('grades/add/', views.grade_add, name='grade_add'),
    path('about/', views.about, name='about'),
    path('api/students/', views.api_students, name='api_students'),  
]