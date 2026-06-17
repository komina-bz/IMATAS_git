from django.db import models

class users(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=50)
    remind_enabled = models.IntegerField()     # 0:OFF, 1:ON
    remind_before_days = models.IntegerField() # 何日前に通知するか
    remind_time = models.TimeField()           # 通知時間
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "users"