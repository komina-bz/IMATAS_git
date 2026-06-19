from django.shortcuts import render

def home(request):
    return render(request, 'tasks/home.html')

def task_list(request):
    return render(request, 'tasks/task_list.html')