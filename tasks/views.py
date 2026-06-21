from accounts.utils import login_required_custom
from django.shortcuts import render, redirect, get_object_or_404
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

    return render(request, 'tasks/add-edit_task.html', context={
        'add_task_form': add_task_form,
    })
    
@login_required_custom
def task_detail_view(request, task_pk):
    # 登録データを取得
    task_data = get_object_or_404(Tasks, pk=task_pk)
    task_form = forms.TaskForm(instance=task_data)
    
    # フォームのすべてのフィールドを読み取り専用（readonly）にする
    for field_name, field in task_form.fields.items():
        field.widget.attrs['readonly'] = True
        # Select（選択肢）やCheckboxはreadonlyが効かないため、
        # 後述のCSS（pointer-events）で操作不能にします。
        # 必要に応じて、ここで「disabled」を付けてもCSSで見た目を上書き可能です。        
    
    return render(request, 'tasks/task_detail.html', context={
        'task_form': task_form,
        'task_data': task_data
    })

@login_required_custom
def edit_task(request, task_pk):
    # 既存データを取得
    task_data = get_object_or_404(Tasks, pk=task_pk)
    
    # 保存ボタンを押されたとき
    if request.method == "POST":
        # 既存データ更新の状態
        edit_task_form = forms.TaskForm(request.POST, request.FILES, instance=task_data)

        # valid → 保存
        if edit_task_form.is_valid():
            edit_task_form.save()  
            return redirect('tasks:task_detail', task_pk=task_pk) # 詳細画面に
    # ページを開いたとき
    else:
        edit_task_form = forms.TaskForm(instance=task_data)

    return render(request, 'tasks/add-edit_task.html', context={
        'add_task_form': edit_task_form,
        'task_data': task_data
    })