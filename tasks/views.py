from django.shortcuts import render, redirect
from . import forms
#from .models import Tasks

def home(request):
    return render(request, 'tasks/home.html')

def task_list(request):
    return render(request, 'tasks/task_list.html')

def add_task(request):
    
    add_task_form = forms.TaskForm(request.POST or None)
    if request.method == 'POST': 
        # valid → 登録
        if add_task_form.is_valid():
            task = add_task_form.save(commit=False)
            task.save()  
            return redirect('tasks:home')

    return render(request, 'tasks/add_task.html', context={
        'add_task_form': add_task_form,
    })