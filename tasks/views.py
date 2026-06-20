from accounts.utils import login_required_custom
from django.shortcuts import render, redirect
from . import forms
from .models import Tasks
from accounts.models import Users
from django.db.models import Max


def home(request):
    return render(request, 'tasks/home.html')

@login_required_custom
def task_list_view(request):
    task_list = Tasks.objects.all()
    return render(request, 'tasks/task_list.html', context={
        'task_list': task_list,
    })

@login_required_custom
def add_task(request):
    add_task_form = forms.TaskForm(request.POST or None)
    if request.method == 'POST': 
        # valid → 登録
        if add_task_form.is_valid():
            task = add_task_form.save(commit=False)
            #ユーザ紐づけ(FK)
            user_id = request.session.get("user_id")
            task.user = Users.objects.get(id=user_id)
            #表示順の登録
            max_display_order = Tasks.objects.aggregate(Max('display_order'))
            if max_display_order['display_order__max'] == None:
                task.display_order = 1
            else:
                task.display_order = max_display_order['display_order__max'] + 1
            task.save()  
            return redirect('tasks:home')

    return render(request, 'tasks/add_task.html', context={
        'add_task_form': add_task_form,
    })