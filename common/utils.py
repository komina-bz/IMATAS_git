from tasks.models import Tasks

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
