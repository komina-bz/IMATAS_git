from django.db import models
from django.utils import timezone

class Users(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
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
    
    
class Password_reset_tokens(models.Model):
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name="password_reset_token",
    )
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "password_reset_tokens"

    def __str__(self):
        return f"{self.user.email}"    