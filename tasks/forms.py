from django import forms
from .models import Tasks

class TaskForm(forms.ModelForm):
    
    class Meta:
        model = Tasks
        fields = ['name', 'memo', 'due_date']
        labels = {
            'name': '名前',
            'memo': 'メモ',
            'due_date': '期限',
        }
