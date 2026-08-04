from tasks.models import Tasks, Condition_sets, Condition_set_items

# 仮登録タスクデータを削除
def delete_temp(request):
    user_id = request.session.get("user_id")
    Tasks.objects.filter(
        user=user_id,
        is_temp_subtask=True,
    ).delete()
    request.session.pop("current_task_pk", None)
    request.session.pop("task_name", None)
    request.session.pop("task_memo", None)
    request.session.pop("task_due_date", None)
    request.session.pop("old_selected", None)
    request.session.pop("old_selected_cond", None)

# 表示順の振りなおし
def reorder_display(request, parent_task):
    # 親タスクなら
    if parent_task is None:
        tasks = list(Tasks.objects.filter(
            user=request.user,
            parent_task__isnull=True,
            status=0,
        ).order_by("display_order")) 
        completed_tasks = list(Tasks.objects.filter(
            user=request.user,
            parent_task__isnull=True,
            status=1,
        ).order_by("display_order")) 
        tasks.extend(completed_tasks)

    # サブタスクなら
    else:
        tasks = list(Tasks.objects.filter(
            user=request.user,
            parent_task=parent_task,
            status=0,
        ).order_by("display_order")) 
        completed_tasks = list(Tasks.objects.filter(
            user=request.user,
            parent_task=parent_task,
            status=1,
        ).order_by("display_order")) 
        tasks.extend(completed_tasks)

    for i, task in enumerate(tasks, start=1):
        task.display_order = i
    Tasks.objects.bulk_update(
        tasks,
        ["display_order"]
    )        


def check_same_conditions_set(request, selected_cond_ids):
    condition_sets = Condition_sets.objects.filter(user=request.user)
    
    for set in condition_sets:
        set_items = Condition_set_items.objects.filter(condition_set_id=set.id)
        set_cond_ids = [item.condition_id for item in set_items]
        # A: set 側の条件が全部 selected に含まれるか
        all_exist = True
        for cond_id in set_cond_ids:
            if cond_id not in selected_cond_ids:
                all_exist = False
                break   
        # B: selected 側に余計な条件がないか
        no_extra = True
        for cond_id in selected_cond_ids:
            if cond_id not in set_cond_ids:
                no_extra = False
                break 
            
        # C: 完全一致かどうか    
        is_same = all_exist and no_extra
        
        if is_same:
            return False
    
    return True