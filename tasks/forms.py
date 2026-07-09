from django import forms
from .models import Tasks, Conditions, Condition_sets

# class TaskForm(forms.Form):
#     task_name = forms.CharField(label="タスク名", max_length=100)
#     task_memo = forms.TextField(label="メモ　　", max_length=100)
#     task_due_date = forms.DateField(label="期限　　", widgets=forms.DateInput(attrs={'type': 'date'}))

class TaskForm(forms.Form):
    task_name = forms.CharField(
        label="タスク名",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    task_memo = forms.CharField(
        label="メモ　　",
        max_length=100,
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control"})
    )

    task_due_date = forms.DateField(
        label="期限　　",
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        })
    )
    

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
