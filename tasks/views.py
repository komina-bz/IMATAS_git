from accounts.utils import login_required_custom
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
    # タスクの登録用フォーム
    add_task_form = forms.TaskForm(request.POST or None)
    # サブタスクの登録用フォーム
    add_subtask_form = forms.SubtaskForm(request.POST or None)
    
    # サブタスク登録後にリダイレクトで戻ってきたとき
    if request.method == "GET":
        # 入力途中のタスクフォームを表示 
        initial_data = {
            "name": request.GET.get("task_name", ""),
            "memo": request.GET.get("task_memo", ""),
            "due_date": request.GET.get("task_due_date", ""),
        }
        add_task_form = forms.TaskForm(initial=initial_data)
        return render(request, "tasks/add-edit_task.html", {
            "add_task_form": add_task_form,
            "add_subtask_form": add_subtask_form,
            })
    
    # いずれかの保存ボタンを押されたとき    
    if request.method == 'POST': 
        action = request.POST.get("action")
        
        # サブタスクの保存ボタンの場合
        if action == "save_subtask":
            if add_subtask_form.is_valid():
                subtask = add_subtask_form.save(commit=False)
                # ユーザ紐づけ(FK)
                user_id = request.session.get("user_id")
                subtask.user = Users.objects.get(id=user_id)
                # 表示順の仮登録
                subtask.display_order = 0
                # サブタスクの仮登録フラグをたてる
                subtask.is_temp_subtask = True
                subtask.save()
                # 編集中のタスク内容を取得
                from urllib.parse import urlencode
                query = urlencode({
                    "task_name": request.POST.get("task_name"),
                    "task_memo": request.POST.get("task_memo"),
                    "task_due_date": request.POST.get("task_due_date"),
                })
                return redirect(f"{reverse('tasks:add_task')}?{query}")

        # タスクの保存ボタンの場合
        elif action == "save_task":      
            # valid → 保存
            if add_task_form.is_valid():
                task = add_task_form.save(commit=False)
                # タスクのユーザ紐づけ(FK)
                user_id = request.session.get("user_id")
                task.user = Users.objects.get(id=user_id)
                # タスクの表示順の登録
                max_display_order = Tasks.objects.aggregate(Max('display_order'))['display_order__max'] or 0
                if max_display_order == 0:
                    task.display_order = 1
                else:
                    task.display_order = max_display_order + 1
                task.save()
                
                # 仮登録サブタスクを取得
                temp_subtasks = Tasks.objects.filter(
                    user = user_id,
                    is_temp_subtask = True
                )
                # 順番にサブタスク登録処理
                for i, subtask in enumerate(temp_subtasks, start=1):
                    subtask.parent_task_id = task.id          # 親タスクの紐づけ(FK)
                    subtask.display_order = i                 # サブタスクの表示順の登録
                    subtask.is_temp_subtask = False           # サブタスク仮登録のフラグを外す
                    subtask.save()
                return redirect('tasks:task_list') # タスクリスト画面に

    return render(request, 'tasks/add-edit_task.html', context={
        'add_task_form': add_task_form,
        'add_subtask_form': add_subtask_form,
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
    # サブタスクの登録用フォーム
    add_subtask_form = forms.SubtaskForm(request.POST or None)

    # サブタスク登録後にリダイレクトで戻ってきたとき
    if request.method == "GET":
        # サブタスク登録後にリダイレクトで戻ってきたとき
        if "task_name" in request.GET or "task_memo" in request.GET or "task_due_date" in request.GET:
            # 入力途中のタスクフォームを表示 
            initial_data = {
                "name": request.GET.get("task_name", ""),
                "memo": request.GET.get("task_memo", ""),
                "due_date": request.GET.get("task_due_date", ""),
            }
            edit_task_form = forms.TaskForm(initial=initial_data)
            
        # ページを開いたとき
        else:
            edit_task_form = forms.TaskForm(instance=task_data)
            
        return render(request, "tasks/add-edit_task.html", {
            "add_task_form": edit_task_form,
            'task_data': task_data,
            "add_subtask_form": add_subtask_form,
            })

    # いずれかの保存ボタンを押されたとき
    if request.method == "POST":
        action = request.POST.get("action")
        
        # サブタスクの保存ボタンの場合
        if action == "save_subtask":
            if add_subtask_form.is_valid():
                subtask = add_subtask_form.save(commit=False)
                # ユーザ紐づけ(FK)
                user_id = request.session.get("user_id")
                subtask.user = Users.objects.get(id=user_id)
                # 表示順の仮登録
                subtask.display_order = 0
                # サブタスクの仮登録フラグをたてる
                subtask.is_temp_subtask = True
                subtask.save()
                # 編集中のタスク内容を取得
                from urllib.parse import urlencode
                query = urlencode({
                    "task_name": request.POST.get("task_name"),
                    "task_memo": request.POST.get("task_memo"),
                    "task_due_date": request.POST.get("task_due_date"),
                })
                return redirect(f"{reverse('tasks:edit_task', args=[task_pk])}?{query}")

        # タスクの保存ボタンの場合
        elif action == "save_task":      
            # 既存データ更新の状態
            edit_task_form = forms.TaskForm(request.POST, request.FILES, instance=task_data)
            # valid → 保存
            if edit_task_form.is_valid():
                # 親タスクの保存
                edit_task_form.save()
                # サブタスクの処理  
                # ユーザidを取得
                user_id = request.session.get("user_id")
                # 既存サブタスクの最大表示順を取得
                max_display_order = Tasks.objects.filter(
                    parent_task_id = task_pk
                ).aggregate(Max('display_order'))['display_order__max'] or 0
                # 仮登録サブタスクを取得
                temp_subtasks = Tasks.objects.filter(
                    user = user_id,
                    is_temp_subtask = True
                )
                # 順番にサブタスク登録処理
                for i, subtask in enumerate(temp_subtasks, start=1):
                    subtask.parent_task_id = task_pk         # 親タスクの紐づけ(FK)
                    if max_display_order == 0:               # 表示順の登録
                        subtask.display_order = 1
                    else:
                        subtask.display_order = max_display_order + i
                    subtask.is_temp_subtask = False          # サブタスク仮登録のフラグを外す
                    subtask.save()

                return redirect('tasks:task_detail', task_pk=task_pk) # 詳細画面に

    return render(request, 'tasks/add-edit_task.html', context={
        'add_task_form': edit_task_form,
        'task_data': task_data,
        'add_subtask_form': add_subtask_form,
    })
    
    
@login_required_custom
def delete_task(request, task_pk):
    # 既存データを取得
    task_data = get_object_or_404(Tasks, pk=task_pk)
    
    # 他人のタスクなら削除させない
    user_id = request.session.get("user_id")
    login_user = Users.objects.get(id=user_id)
    if task_data.user != login_user:
        return redirect('tasks:task_list')
    
    if request.method == "POST":
        task_data.delete()
        return redirect('tasks:task_list')
    
    return redirect('tasks:task_detail', task_pk=task_pk)