from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from journal.models import (User, Group, Student, Teacher, Subject, 
                            TeachingLoad, Lesson, Grade)

class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начинаем заполнение базы...')

        # 1. Создаем куратора
        curator, _ = User.objects.get_or_create(username='curator1', defaults={'first_name': 'Ольга', 'last_name': 'Кураторова', 'role': 'curator'})
        curator.set_password('12345')
        curator.save()

        # 2. Создаем группы
        g1, _ = Group.objects.get_or_create(name='ИС-21', defaults={'specialty': 'Информационные системы', 'course': 2, 'curator': curator})
        g2, _ = Group.objects.get_or_create(name='ПР-22', defaults={'specialty': 'Программирование', 'course': 1, 'curator': curator})

        # 3. Создаем студентов
        names = [('Иван', 'Иванов'), ('Пётр', 'Петров'), ('Анна', 'Сидорова'), ('Алексей', 'Кузнецов'), ('Ольга', 'Смирнова')]
        students = []
        for i, (first, last) in enumerate(names, 1):
            user, _ = User.objects.get_or_create(username=f'student{i}', defaults={'first_name': first, 'last_name': last, 'role': 'student'})
            user.set_password('12345')
            user.save()
            student, _ = Student.objects.get_or_create(user=user, defaults={'group': g1 if i % 2 else g2, 'record_book': f'ЗК-{1000+i}', 'birth_date': date(2005, (i % 12) + 1, (i % 27) + 1)})
            students.append(student)

        # 4. Создаем преподавателя
        t_user, _ = User.objects.get_or_create(username='teacher1', defaults={'first_name': 'Игорь', 'last_name': 'Учителев', 'role': 'teacher'})
        t_user.set_password('12345')
        t_user.save()
        teacher, _ = Teacher.objects.get_or_create(user=t_user, defaults={'position': 'Старший преподаватель'})

        # 5. Создаем предметы и нагрузки
        subjects = []
        for name, code, sem in [('Математика', 'MATH01', 1), ('Программирование', 'PROG01', 1), ('Базы данных', 'DB01', 2)]:
            s, _ = Subject.objects.get_or_create(code=code, defaults={'name': name, 'semester': sem})
            subjects.append(s)

        # 6. Создаем занятия и оценки
        for subject in subjects:
            load, _ = TeachingLoad.objects.get_or_create(teacher=teacher, subject=subject, group=g1)
            for week in range(3):
                lesson_date = date.today() - timedelta(days=7 * week)
                lesson, _ = Lesson.objects.get_or_create(date=lesson_date, pair_number=1, load=load, defaults={'topic': f'Тема {week + 1}', 'lesson_type': 'lecture'})
                
                for student in students:
                    if student.group == g1:
                        Grade.objects.get_or_create(student=student, lesson=lesson, defaults={'value': random.randint(3, 5), 'grade_type': 'current', 'date': lesson_date})

        self.stdout.write(self.style.SUCCESS('База успешно заполнена!'))