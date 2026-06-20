from django import forms
from .models import Tasks

class TaskForm(forms.ModelForm):
    
    class Meta:
        model = Tasks
        fields = ['name', 'memo', 'due_date']
        labels = {
            'name': 'タスク名',
            'memo': 'メモ　　',
            'due_date': '期限　　',
        }
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
