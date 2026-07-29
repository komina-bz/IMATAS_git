from tasks.models import Tasks

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
