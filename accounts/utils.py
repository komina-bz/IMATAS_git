from django.shortcuts import redirect
from .models import Users
from tasks.models import Tasks
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from datetime import timedelta
from django.conf import settings
import requests


def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("accounts:login")

        # ★ここが重要：request.user に Users インスタンスをセット
        request.user = Users.objects.get(id=user_id)

        return view_func(request, *args, **kwargs)
    return wrapper


def send_brevo_email(to_email, subject, text_content):
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        json={
            "sender": {
                "name": "IMATAS",
                "email": settings.DEFAULT_FROM_EMAIL,
            },
            "to": [
                {
                    "email": to_email,
                }
            ],
            "replyTo": {
                "email": settings.BREVO_REPLY_TO,
            },
            "subject": subject,
            "textContent": text_content,
        },
    )

    print(response.status_code)
    print(response.text)

    return response.status_code == 201


def send_notification_mail():
    now = timezone.localtime()
    today = now.date()   # 日付
    current_time = now.time().replace(second=0, microsecond=0)  # 時間

    # 通知時刻が current_time と一致するユーザーを抽出
    users = Users.objects.filter(
        remind_enabled=1,     # 1:ON
        remind_time=current_time, 
        )

    for user in users:
        # ユーザーの通知対象となる期限を算出
        due_date_reminded = today + timedelta(days=user.remind_before_days)
        # 通知対象となる未完了タスクを抽出
        tasks_reminded = Tasks.objects.filter(
            user_id=user.id,
            due_date=due_date_reminded,
            status=0,
            )        
        
        if tasks_reminded:
            # 期限超過の未完了タスクを抽出
            expired_tasks = Tasks.objects.filter(
                user_id=user.id,
                due_date__lt=today,
                status=0,
                )
            # 期限の表示を整える
            expired_tasks_reminded = []
            for task in expired_tasks:
                diff_over = abs((task.due_date - today).days)
                display_due = f"{diff_over}日超過"
                # タスクに新しい属性を付けてテンプレートへ渡す
                task.display_due = display_due    
                expired_tasks_reminded.append(task)
            # 通知対象となる期限以前に期限を迎える未完了タスクを抽出
            upcoming_tasks_reminded = Tasks.objects.filter(
                user_id=user.id,
                due_date__gte=today,
                due_date__lt=due_date_reminded,
                status=0,
                )
            
            # 件名の作成
            if user.remind_before_days == 0:
                subj = f"【いまタス】本日中に期限を迎えるタスクがあります"
            else:
                subj = f"【いまタス】{user.remind_before_days}日後に期限を迎えるタスクがあります"
            # 本文の作成
            upcoming_tasks_count = upcoming_tasks_reminded.count() 
            imatas_url = "(URLを貼る)"
            
            message = "\n"
            if user.remind_before_days == 0:
                message += f"■ 本日中に期限を迎えるタスク\n"
            else:
                message += f"■ {user.remind_before_days}日後に期限を迎えるタスク\n"
            for task in tasks_reminded:
                parent_name = getattr(task.parent_task, "name", "")
                message += f"- {task.name.ljust(30)} ({parent_name.ljust(20)})\n"        
            message += f"\n■ 期限超過\n"
            for task in expired_tasks_reminded:
                parent_name = getattr(task.parent_task, "name", "")
                if task.parent_task_id is None:
                    message += f"- {task.name.ljust(30)} : {task.display_due.ljust(10)}\n"        
                else:
                    message += f"- {task.name.ljust(30)} ({parent_name.ljust(20)}) : {task.display_due.ljust(10)}\n"        
            if user.remind_before_days != 0:
                message += f"\n■ その他\n"
                message += f"今後{user.remind_before_days}日以内に期限を迎える未完了タスクが{upcoming_tasks_count}件あります\n".lstrip()
            message += f"\n≫いまタスで確認する\n"
            message += f"{imatas_url}\n".lstrip()

            # メール送信
            send_brevo_email(
                to_email=user.email,
                subject=subj,
                text_content=message,
            )    
            
