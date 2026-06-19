from django.shortcuts import render

def home(request):
    return render(request, 'tasks/home.html')

def task_list(request):
    return render(request, 'tasks/task_list.html')

def add_task(request):
    return render(request, 'tasks/add_task.html')