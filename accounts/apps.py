import os
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

class AccountsConfig(AppConfig):
    name = 'accounts'

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return  # ← メインプロセスでは起動しない        
        
        from accounts.utils import send_notification_mail
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_notification_mail, 'interval', minutes=1)
        scheduler.start()