from django import forms
from .models import Grade

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'lesson', 'value', 'grade_type', 'date']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}