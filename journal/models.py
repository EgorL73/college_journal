from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('parent', 'Родитель'),
        ('teacher', 'Преподаватель'),
        ('curator', 'Куратор'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Group(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    specialty = models.CharField('Специальность', max_length=100)
    course = models.IntegerField('Курс', validators=[MinValueValidator(1), MaxValueValidator(4)])
    curator = models.ForeignKey(User, verbose_name='Куратор', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='curated_groups',
                                limit_choices_to={'role': 'curator'})

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE,
                                 related_name='student_profile', limit_choices_to={'role': 'student'})
    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.PROTECT,
                              related_name='students')
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    record_book = models.CharField('Зачётная книжка', max_length=20, unique=True)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['user__last_name']

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name}'


class Parent(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE,
                                 related_name='parent_profile', limit_choices_to={'role': 'parent'})
    phone = models.CharField('Телефон', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Родитель'
        verbose_name_plural = 'Родители'

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name}'


class ParentStudent(models.Model):
    RELATION = [('mother', 'Мать'), ('father', 'Отец'), ('guardian', 'Опекун')]
    parent = models.ForeignKey(Parent, verbose_name='Родитель', on_delete=models.CASCADE,
                                related_name='children_links')
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.CASCADE,
                                 related_name='parent_links')
    relation = models.CharField('Родство', max_length=20, choices=RELATION)

    class Meta:
        verbose_name = 'Связь родитель–студент'
        verbose_name_plural = 'Связи родитель–студент'
        constraints = [models.UniqueConstraint(fields=['parent', 'student'], name='unique_parent_student')]

    def __str__(self):
        return f'{self.parent} → {self.student}'


class Teacher(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE,
                                 related_name='teacher_profile', limit_choices_to={'role': 'teacher'})
    position = models.CharField('Должность', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name}'


class Subject(models.Model):
    name = models.CharField('Название', max_length=100)
    code = models.CharField('Код', max_length=20, unique=True)
    semester = models.IntegerField('Семестр', validators=[MinValueValidator(1), MaxValueValidator(8)])

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['name']

    def __str__(self):
        return self.name


class TeachingLoad(models.Model):
    teacher = models.ForeignKey(Teacher, verbose_name='Преподаватель', on_delete=models.CASCADE,
                                 related_name='loads')
    subject = models.ForeignKey(Subject, verbose_name='Предмет', on_delete=models.CASCADE,
                                 related_name='loads')
    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE,
                               related_name='loads')

    class Meta:
        verbose_name = 'Нагрузка'
        verbose_name_plural = 'Нагрузки'
        constraints = [models.UniqueConstraint(fields=['teacher', 'subject', 'group'], name='unique_load')]

    def __str__(self):
        return f'{self.teacher} — {self.subject} ({self.group})'


class Lesson(models.Model):
    TYPE = [('lecture', 'Лекция'), ('practice', 'Практика')]
    date = models.DateField('Дата')
    pair_number = models.IntegerField('Пара', validators=[MinValueValidator(1), MaxValueValidator(7)])
    load = models.ForeignKey(TeachingLoad, verbose_name='Нагрузка', on_delete=models.CASCADE,
                              related_name='lessons')
    topic = models.CharField('Тема', max_length=200, blank=True)
    lesson_type = models.CharField('Тип', max_length=20, choices=TYPE)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['-date', 'pair_number']

    def __str__(self):
        return f'{self.date} — {self.load.subject}'


class Grade(models.Model):
    TYPE = [('current', 'Текущая'), ('control', 'Контрольная'), ('final', 'Итоговая')]
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.CASCADE,
                                 related_name='grades')
    lesson = models.ForeignKey(Lesson, verbose_name='Занятие', on_delete=models.CASCADE,
                                related_name='grades')
    value = models.IntegerField('Оценка', validators=[MinValueValidator(2), MaxValueValidator(5)])
    grade_type = models.CharField('Тип', max_length=20, choices=TYPE)
    comment = models.TextField('Комментарий', max_length=500, blank=True)
    date = models.DateField('Дата')

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['-date']
        constraints = [
            models.CheckConstraint(condition=models.Q(value__gte=2) & models.Q(value__lte=5), name='grade_2_5'),
            models.UniqueConstraint(fields=['student', 'lesson'], name='unique_grade'),
        ]

    def __str__(self):
        return f'{self.student} — {self.value}'


class Absence(models.Model):
    REASON = [('valid', 'Уважительная'), ('invalid', 'Неуважительная'), ('unknown', 'Не указана')]
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.CASCADE,
                                 related_name='absences')
    lesson = models.ForeignKey(Lesson, verbose_name='Занятие', on_delete=models.CASCADE,
                                related_name='absences')
    reason = models.CharField('Причина', max_length=20, choices=REASON, default='unknown')
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        verbose_name = 'Пропуск'
        verbose_name_plural = 'Пропуски'
        constraints = [models.UniqueConstraint(fields=['student', 'lesson'], name='unique_absence')]

    def __str__(self):
        return f'{self.student} — {self.lesson.date}'


class Schedule(models.Model):
    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE,
                               related_name='schedule')
    day_of_week = models.IntegerField('День', validators=[MinValueValidator(1), MaxValueValidator(6)])
    pair_number = models.IntegerField('Пара', validators=[MinValueValidator(1), MaxValueValidator(7)])
    load = models.ForeignKey(TeachingLoad, verbose_name='Нагрузка', on_delete=models.CASCADE,
                              related_name='schedule')
    room = models.CharField('Аудитория', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['day_of_week', 'pair_number']
        constraints = [models.UniqueConstraint(fields=['group', 'day_of_week', 'pair_number'],
                                                name='unique_slot')]

    def __str__(self):
        return f'{self.group} — день {self.day_of_week}, пара {self.pair_number}'


# --- Дополнительные свойства для шаблонов (добавлено для Занятия 7) ---
from django.urls import reverse

Student.full_name = property(
    lambda self: f'{self.user.last_name} {self.user.first_name}'.strip()
)
Student.get_absolute_url = property(
    lambda self: reverse('journal:student', args=[self.pk])
)
Student.average_grade = property(
    lambda self: (round(sum(g.value for g in self.grades.all()) / self.grades.count(), 2) if self.grades.exists() else None)
)
Grade.subject = property(lambda self: self.lesson.load.subject)