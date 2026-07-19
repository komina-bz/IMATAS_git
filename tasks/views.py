from accounts.utils import login_required_custom
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from . import forms
from .models import Tasks, Task_conditions, Conditions, Condition_categories, Condition_sets, Condition_set_items
from accounts.models import Users
from django.db.models import Max
from datetime import date
from django.utils import timezone
from datetime import timedelta
import json

@login_required_custom
def home(request):
    
    # DBから仮登録中のサブタスクを消す（保存せずに遷移してきたときの対策）
    if request.method == "GET":
        user_id = request.session.get("user_id")
        Tasks.objects.filter(
            user=user_id,
            is_temp_subtask=True,
        ).delete()


    # 期限があるタスクを近いものから3件抽出
    user_id = request.session.get("user_id")
    ordered_3tasks_by_due = []
    # 期限があるタスクを期限順に並べる
    tasks_by_due_all = Tasks.objects.filter(
        user=user_id,
        due_date__isnull=False
    ).order_by('due_date') 
    # 期限の表示を整え、近いものから3件抽出
    count = 0
    count_timeout = 0
    for t in tasks_by_due_all:
        diff = (t.due_date - date.today()).days      
        if diff >= 0:
            if count < 3:
                count = count + 1
                if diff == 0:
                    display_due = "当日"
                elif diff == 1:
                    display_due = "明日"
                elif diff == 2 or diff == 3:
                    display_due = f"{diff}日以内"
                else:
                    display_due = t.due_date.strftime("%Y-%m-%d")
                # タスクに新しい属性を付けてテンプレートへ渡す
                t.display_due = display_due   
                ordered_3tasks_by_due.append(t)
        else:
            count_timeout = count_timeout + 1
    if count_timeout >= 0:
        num_of_timeout_task = count_timeout
    else:
        num_of_timeout_task = None
    
    # よく使う状況を取得    
    condition_set_list = Condition_sets.objects.filter(user_id=user_id)
    selected_set_ids = [] 
    active_condition_ids = [] 
    
    # カテゴリー情報を取得（状況ボタン表示用）
    categories = Condition_categories.objects.all()

    if request.method == "GET":
        origin = request.session.get("origin", [])
        selected_s = request.session.get("selected_set_ids", [])  
        selected_c = request.session.get("selected_cond", [])  
        
        # よく使う状況ボタンの押下で戻ってきたとき
        # 紐づいた状況ボタンもアクティブにする
        if origin == "set2cond":                    
            new_selected_set_ids = [int(x) for x in selected_s if str(x).isdigit()] 
            old_selected_set_ids = request.session.get("old_selected", [])  
            old_selected_set_ids = [int(x) for x in old_selected_set_ids if str(x).isdigit()] 
            # 新しく選択されたボタン
            selected_set_ids = [sid for sid in new_selected_set_ids if sid not in old_selected_set_ids]
            
            active_condition_ids = list(
                Condition_set_items.objects.filter(
                    condition_set__user_id=user_id,
                    condition_set_id__in=selected_set_ids
                ).values_list("condition_id", flat=True)
            )
            # 今の選択状況をsessionに保存
            request.session["old_selected"] = selected_set_ids
            request.session["old_selected_cond"] = active_condition_ids
            
            # # sessionに値が入っていれば消す
            request.session.pop("origin", None)
            request.session.pop("selected_set_ids", None)
            request.session.pop("selected_cond", None)
        
        # 状況ボタンの押下で戻ってきたとき
        # 紐づいたよく使う状況ボタンがあればアクティブを消す
        elif origin == "cond_active" or origin == "cond_unactive":
            selected_set_ids = [int(x) for x in selected_s if str(x).isdigit()] 
            active_condition_ids = [int(x) for x in selected_c if str(x).isdigit()] 
            if selected_set_ids:
                selected_set_ids = []
            
            # 同じカテゴリで1つだけ。他の選択があった場合は選択を消す
            if origin == "cond_active":
                old_selected_cond_ids = request.session.get("old_selected_cond", [])  
                old_selected_cond_ids = [int(x) for x in old_selected_cond_ids if str(x).isdigit()] 
                # 新しく選択されたボタン
                new_selected_cond_id = [cid for cid in active_condition_ids if cid not in old_selected_cond_ids]
                # 同じカテゴリーの既存選択を除外
                new_selected_cond = Conditions.objects.get(id=new_selected_cond_id[0])
                filtered_selected = []
                for cid in active_condition_ids:
                    c = Conditions.objects.get(id=cid)
                    if c.condition_category_id != new_selected_cond.condition_category_id:
                        filtered_selected.append(cid)
                # 新しく選択された状況を追加
                filtered_selected.append(new_selected_cond_id[0])  
                active_condition_ids = filtered_selected

            # 今の選択状況をsessionに保存
            request.session["old_selected"] = selected_set_ids
            request.session["old_selected_cond"] = active_condition_ids

            # # sessionに値が入っていれば消す
            request.session.pop("origin", None)
            request.session.pop("selected_set_ids", None)
            request.session.pop("selected_cond", None)
        
        # 他のページからの遷移やページ更新などの時は
        # 選択状態をリセット    
        else:
            # sessionに値が入っていれば消す
            request.session.pop("matched_task_ids", None)
            request.session.pop("selected_cond_ids", None)
            request.session.pop("selected_set_ids", None)
    
    elif request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")
        
        # よく使う状況ボタンが押された場合
        if action == "link_set2cond":
            request.session["origin"] = "set2cond"
            request.session["selected_set_ids"] = data.get("new_selected_set_ids")
            
        # 状況ボタンのactiveになった場合
        elif action == "cond_active":
            request.session["origin"] = "cond_active"
            request.session["selected_set_ids"] = data.get("selected_set_ids")  
            request.session["selected_cond"] = data.get("selected_cond")  
            
        # 状況ボタンのactiveが外された場合
        elif action == "cond_unactive":
            request.session["origin"] = "cond_unactive"
            request.session["selected_set_ids"] = data.get("selected_set_ids")  
            request.session["selected_cond"] = data.get("selected_cond")  
                         
        # いまタスを見るボタンが押された場合     
        elif action == "search_task":
            selected_set_ids = data.get("selected_set_ids", [])
            selected_set_ids = [int(x) for x in selected_set_ids]
            selected_cond_ids = data.get("selected_cond_ids", [])
            selected_cond_ids = [int(x) for x in selected_cond_ids]
            # Task_conditionsをすべて取得
            tc_list = Task_conditions.objects.filter(
                task__user_id=request.user.id,
                condition__user_id=request.user.id
            )
            # タスクごとに状況を整理
            task_to_conditions = {}
            for tc in tc_list:
                if tc.task_id not in task_to_conditions:
                    task_to_conditions[tc.task_id] = []
                task_to_conditions[tc.task_id].append(tc.condition_id)
            # 選択された状況と、同じ数で同じ要素を持つものだけ残す
            matched_task_ids = []
            for task_id, cond_ids in task_to_conditions.items():
                if sorted(cond_ids) == sorted(selected_cond_ids):
                    matched_task_ids.append(task_id)
            
            # よく使う状況の使用頻度のカウント(状況が2つ以上の場合)
            # -- 保存されていない状況の組み合わせは
            # -- 直近1ヶ月で3回以上使ったものは自動表示。
            # -- 直近1ヶ月で使用されなかったらDBから削除。
            if len(selected_cond_ids) > 2:
                # よく使う状況ボタンが押された場合
                if selected_set_ids:
                    selected_set = Condition_sets.objects.get(
                        user_id=user_id,
                        id=selected_set_ids[0]
                        )
                # よく使う状況ボタンが押されていない場合
                else:
                    # 自動表示されるCondition_set_itemsをすべて取得
                    items_list = Condition_set_items.objects.filter(
                        condition_set__user_id=request.user.id,
                        condition__user_id=request.user.id,
                    )
                    # 自動表示の保存状況ごとに状況を整理
                    set_to_conditions = {}
                    for item in items_list:
                        set_id = item.condition_set_id
                        cond_id = item.condition_id     
                        if set_id not in set_to_conditions:
                            set_to_conditions[set_id] = []
                        set_to_conditions[set_id].append(cond_id)
                    # 選択された状況と、同じ数で同じ要素を持つものだけ残す
                    matched_set_ids = []
                    for set_id, cond_ids in set_to_conditions.items():
                        if sorted(cond_ids) == sorted(selected_cond_ids):
                            matched_set_ids.append(set_id)
                    
                    # 保存状況と一致する組み合わせの場合
                    if matched_set_ids:
                        selected_set = Condition_sets.objects.get(id=matched_set_ids[0])
                    # 保存状況にはない組み合わせの場合
                    else:
                        # Condition_setsを新規作成
                        cond_names = list(
                            Conditions.objects.filter(id__in=selected_cond_ids)
                                            .values_list("name", flat=True)
                        )
                        set_name = " × ".join(cond_names)
                        selected_set = Condition_sets.objects.create(
                            user_id = request.user.id,
                            name = set_name,
                        )
                        # Condition_set_itemsを新規作成
                        for cond_id in selected_cond_ids:
                            Condition_set_items.objects.create(
                                condition_set=selected_set,
                                condition_id=cond_id
                            )    
                # 使用履歴と回数カウントの保存    
                selected_set.use_count = selected_set.use_count + 1
                selected_set.last_use_at = timezone.now()
                selected_set.save()
            
            # 自動表示の中で、直近1ヶ月に使用されていないものは削除する
            one_month_ago = timezone.now() - timedelta(days=30)
            Condition_sets.objects.filter(
                set_type=0,
                last_use_at__lt=one_month_ago
            ).delete()
            
            # リダイレクトのためsessionに保存
            request.session["matched_task_ids"] = matched_task_ids
            request.session["selected_cond_ids"] = selected_cond_ids
            request.session["selected_set_ids"] = selected_set_ids
            return redirect("tasks:imatas_result")
        
    
    return render(request, 'tasks/home.html', context={
        'tasks_by_due': ordered_3tasks_by_due,
        'num_of_timeout_task': num_of_timeout_task,
        "condition_set_list": condition_set_list,
        "categories": categories,
        "user_id": user_id,
        "selected_set_ids": selected_set_ids,
        "active_condition_ids": active_condition_ids,
    })
    
@login_required_custom
def imatas_result(request):
    user_id = request.session.get("user_id")
    matched_task_ids = request.session.get("matched_task_ids", [])
    selected_cond_ids = request.session.get("selected_cond_ids", [])
    selected_set_ids = request.session.get("selected_set_ids", [])
    
    imatas = Tasks.objects.filter(id__in=matched_task_ids)
    
    # 期限の表示を整える
    for t in imatas:
        diff = (t.due_date - date.today()).days
        if diff < 0:
            diff_over = abs(diff)
            display_due = f"{diff_over}日超過"
        elif diff == 0:
            display_due = "当日"
        elif diff == 1:
            display_due = "明日"
        elif diff == 2 or diff == 3:
            display_due = f"{diff}日以内"
        else:
            display_due = t.due_date.strftime("%Y-%m-%d")
        # タスクに新しい属性を付ける
        t.display_due = display_due    
    
    selected_cond_list = Conditions.objects.filter(
        user_id=user_id,
        id__in=selected_cond_ids
        )
    
    if selected_set_ids:
        selected_set = Condition_sets.objects.get(
            user_id=user_id,
            id=selected_set_ids[0]
            )
    else:
        selected_set = None
        
        
    return render(request, 'tasks/imatas_result.html', context={
        "imatas": imatas,
        "selected_cond_list": selected_cond_list,
        "selected_set": selected_set
    })
    

@login_required_custom
def task_list_view(request):
    user_id = request.session.get("user_id")

    # DBから仮登録中のサブタスクを消す（保存せずに遷移してきたときの対策）
    if request.method == "GET":
        Tasks.objects.filter(
            user=user_id,
            is_temp_subtask=True,
        ).delete()
        
    # DBから親リスト取得
    ordered_parent_tasks = Tasks.objects.filter(
        user=user_id, 
        parent_task__isnull=True
    ).order_by('display_order')
    ordered_tasks = []
    # 表示順に並び替え
    for parent in ordered_parent_tasks:
        ordered_tasks.append(parent)
        # サブタスクの追加
        subtasks = Tasks.objects.filter(
            user=user_id, 
            parent_task=parent
        ).order_by('display_order')
        for s in subtasks:
            ordered_tasks.append(s)     
    
    return render(request, 'tasks/task_list.html', context={
        'task_list': ordered_tasks,
    })

@login_required_custom
def task_list_by_due(request):
    user_id = request.session.get("user_id")
    
    ordered_tasks_by_due = []
    # 期限があるタスクを期限順に並べる
    tasks_by_due = Tasks.objects.filter(
        user=user_id,
        due_date__isnull=False
    ).order_by('due_date') 
    # 期限の表示を整える
    for t in tasks_by_due:
        diff = (t.due_date - date.today()).days
        if diff < 0:
            diff_over = abs(diff)
            display_due = f"{diff_over}日超過"
        elif diff == 0:
            display_due = "当日"
        elif diff == 1:
            display_due = "明日"
        elif diff == 2 or diff == 3:
            display_due = f"{diff}日以内"
        else:
            display_due = t.due_date.strftime("%Y-%m-%d")
        # タスクに新しい属性を付けてテンプレートへ渡す
        t.display_due = display_due    
        ordered_tasks_by_due.append(t)
    # 期限がないタスクを表示順に並べる
    parent_tasks_no_due = Tasks.objects.filter(
        user=user_id, 
        due_date__isnull=True,
        parent_task__isnull=True
    ).order_by('display_order')
    for parent in parent_tasks_no_due:
        # 親タスクの追加
        ordered_tasks_by_due.append(parent)
        # サブタスクの追加
        subtasks = Tasks.objects.filter(
            user=user_id, 
            due_date__isnull=True,
            parent_task=parent,
        ).order_by('display_order')
        for s in subtasks:
            ordered_tasks_by_due.append(s)  
                     
    return render(request, 'tasks/task_list_by_due.html', context={
        'tasks_by_due': ordered_tasks_by_due,
    })
    
@login_required_custom
def task_detail_view(request, task_pk):
    user_id = request.session.get("user_id")
    
    # DBから仮登録中のサブタスクを消す（保存せずに遷移してきたときの対策）
    if request.method == "GET":
        Tasks.objects.filter(
            user=user_id,
            is_temp_subtask=True,
        ).delete()
        
    # 登録データを取得
    task_data = get_object_or_404(Tasks, pk=task_pk)
    task_form = forms.TaskForm(initial={
        "task_name": task_data.name,
        "task_memo": task_data.memo,
        "task_due_date": task_data.due_date,
    })            
    
    # フォームのすべてのフィールドを読み取り専用（readonly）にする
    for field_name, field in task_form.fields.items():
        field.widget.attrs['readonly'] = True
        # Select（選択肢）やCheckboxはreadonlyが効かないため、
        # 後述のCSS（pointer-events）で操作不能にします。
        # 必要に応じて、ここで「disabled」を付けてもCSSで見た目を上書き可能です。        
    
    # サブタスクを取得し、表示順に並べる
    subtasks = Tasks.objects.filter(
        user=user_id, 
        parent_task_id = task_pk
    ).order_by('display_order')
    
    return render(request, 'tasks/task_detail.html', context={
        'task_form': task_form,
        'task_data': task_data,
        'subtasks': subtasks,        
    })
    
@login_required_custom
def update_task(request, task_pk=None): # task_pk があれば編集、なければ追加
    user_id = request.session.get("user_id")
    if task_pk:
        # 既存データを取得
        task_data = get_object_or_404(Tasks, pk=task_pk) 
        # 登録されている状況を取得
        set_data = Task_conditions.objects.filter(task_id=task_pk)
        if set_data == None:
            existing_cond_ids = None
        else:
            existing_cond_ids = []
            for s in set_data:
                existing_cond_ids.append(s.condition_id)
    else:
        task_data = Tasks.objects.create(
            name="",
            user=request.user,
            display_order = 0,
            is_temp_subtask=True,   # 仮保存フラグ
        )
        existing_cond_ids = None
        
    # サブタスクの登録用フォーム
    add_subtask_form = forms.SubtaskForm(request.POST or None)

    # サブタスクを取得し、表示順に並べる
    if task_data.parent_task is None:
        subtasks = Tasks.objects.filter(
            user=user_id,
            parent_task_id = task_pk
            ).order_by('display_order')
    else:
        subtasks = []
        
    # カテゴリー情報を取得（ボタン表示用）
    categories = Condition_categories.objects.all()     
    
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
            task_form = forms.TaskForm(initial=initial_data)
            
        # ページを開いたとき
        else:
            task_form = forms.TaskForm(initial={
                "task_name": task_data.name,
                "task_memo": task_data.memo,
                "task_due_date": task_data.due_date,
            })            
        return render(request, "tasks/add-edit_task.html", {
            "add_task_form": task_form,
            'task_data': task_data,
            "add_subtask_form": add_subtask_form,
            'subtasks': subtasks, 
            "categories": categories,
            "user_id": user_id,
            "selected_ids": existing_cond_ids,
        })

    # いずれかの保存ボタンを押されたとき
    if request.method == "POST":
        action = request.POST.get("action")
        
        # サブタスクの保存ボタンの場合
        if action == "save_subtask":
            if add_subtask_form.is_valid():
                subtask = add_subtask_form.save(commit=False)
                # ユーザ紐づけ(FK)
                subtask.user = Users.objects.get(id=user_id)
                # 表示順の仮登録
                max_display_order = Tasks.objects.filter(
                    user=user_id,
                    parent_task_id = task_data.id
                ).aggregate(Max('display_order'))['display_order__max'] or 0
                subtask.display_order = max_display_order + 1
                # サブタスクの仮登録フラグをたてる
                subtask.is_temp_subtask = True
                subtask.parent_task_id = task_data.id
                subtask.save()
                
            # 編集中の親タスク内容を取得
            from urllib.parse import urlencode
            query = urlencode({
                "task_name": request.POST.get("task_name"),
                "task_memo": request.POST.get("task_memo"),
                "task_due_date": request.POST.get("task_due_date"),
            })
            
            if task_pk:
                return redirect(f"{reverse('tasks:edit_task', args=[task_pk])}?{query}")
            else:
                return redirect(f"{reverse('tasks:add_task')}?{query}")

        # 親タスクの保存ボタンの場合
        elif action == "save_task":
            # 既存データ更新の状態
            task_form = forms.TaskForm(request.POST or None, initial={
                "task_name": task_data.name,
                "task_memo": task_data.memo,
                "task_due_date": task_data.due_date,
            })
            # valid → 保存
            if task_form.is_valid():
                # 親タスク登録
                task_data.name = task_form.cleaned_data["task_name"]
                task_data.memo = task_form.cleaned_data["task_memo"] or None
                task_data.due_date = task_form.cleaned_data["task_due_date"]
                if task_pk == None:
                    # タスクの表示順の登録
                    max_display_order = Tasks.objects.filter(
                        user=user_id,
                        parent_task_id__isnull = True
                    ).aggregate(Max('display_order'))['display_order__max'] or 0
                    task_data.display_order = max_display_order + 1
                task_data.is_temp_subtask = False    
                task_data.save()            
                
                # サブタスク本登録
                # 既存サブタスクの最大表示順を取得
                max_display_order = Tasks.objects.filter(
                    user=user_id,
                    parent_task_id = task_data.id
                ).aggregate(Max('display_order'))['display_order__max'] or 0
                # 仮登録サブタスクを取得
                temp_subtasks = Tasks.objects.filter(
                    user = user_id,
                    parent_task_id = task_data.id,
                    is_temp_subtask = True,
                )
                # 順番にサブタスク登録処理
                for i, subtask in enumerate(temp_subtasks, start=1):
                    subtask.display_order = max_display_order + i # 表示順の登録
                    subtask.is_temp_subtask = False          # サブタスク仮登録のフラグを外す
                    subtask.save()
                    
                # 状況の登録
                # 選択されたボタン(状況)を取得
                selected = request.POST.get("selected_conditions", "")
                selected_cond_ids = selected.split(",") if selected else []
                # 編集なら既存の状況で、新しい状況にふくまれていないものを削除
                if task_pk and existing_cond_ids:
                    for cond_id in existing_cond_ids:
                        if cond_id not in selected_cond_ids:
                            item = Task_conditions.objects.filter(
                                task_id = task_pk,
                                condition_id = cond_id,
                            )
                            item.delete() 
                # 新しい状況をtask_conditionsに保存
                for cond_id in selected_cond_ids:
                    Task_conditions.objects.get_or_create(
                        task = task_data,
                        condition = Conditions.objects.get(id=cond_id),
                    )      

                if task_pk:
                    return redirect('tasks:task_detail', task_pk=task_pk) # 詳細画面に
                else:
                    return redirect('tasks:task_list') # タスクリスト画面に

    task_form = forms.TaskForm(initial={
        "task_name": task_data.name,
        "task_memo": task_data.memo,
        "task_due_date": task_data.due_date,
    })            
    
    return render(request, 'tasks/add-edit_task.html', context={
        'add_task_form': task_form,
        'task_data': task_data,
        'add_subtask_form': add_subtask_form,
        'subtasks': subtasks,       
        "categories": categories,
        "user_id": user_id,
        "selected_ids": existing_cond_ids,
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