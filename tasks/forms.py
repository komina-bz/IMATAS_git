from django import forms
from .models import Tasks, Conditions, Condition_sets

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

class SubtaskForm(forms.ModelForm):
    
    class Meta:
        model = Tasks
        fields = ['name', 'due_date']
        labels = {
            'name': 'タスク名',
            'due_date': '期限　　',
        }
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ConditionForm(forms.ModelForm):
    
    class Meta:
        model = Conditions
        fields = ['name']
        labels = {
            'name': '状況名',
        }

class ConditionSetForm(forms.ModelForm):
    
    class Meta:
        model = Condition_sets
        fields = ['name']
        labels = {
            'name': '状況名',
        }
