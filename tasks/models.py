from django.db import models
from accounts.models import Users

class Tasks(models.Model):
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="tasks")
    parent_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, 
        null=True, blank=True, related_name="subtasks"
        )
    name = models.CharField(max_length=100)
    memo = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=0)    # 0:未完了, 1:完了
    display_order = models.IntegerField()      # タスク一覧表示順番
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "tasks"
        
    def __str__(self):
        return self.name