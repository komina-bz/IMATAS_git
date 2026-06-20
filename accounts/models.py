from django.db import models

class Users(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=50)
    remind_enabled = models.IntegerField(default=0)     # 0:OFF, 1:ON
    remind_before_days = models.IntegerField(default=0) # 何日前に通知するか
    remind_time = models.TimeField(default="00:00:00")  # 通知時間
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "users"
        
    def __str__(self):
        return self.name        