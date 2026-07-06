from django.db import models
from accounts.models import Users

class Tasks(models.Model):
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="tasks")
    parent_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, 
        null=True, default=None, related_name="subtasks"
        )
    name = models.CharField(max_length=100)
    memo = models.TextField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(default=0)    # 0:未完了, 1:完了
    display_order = models.IntegerField()      # タスク一覧表示順番
    is_temp_subtask = models.BooleanField(default=False) # サブタスク仮登録状態
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "tasks"
        
    def __str__(self):
        return self.name
    
class Condition_categories(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "condition_categories"
        
    def __str__(self):
        return self.name    
    
class Conditions(models.Model):
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="conditions")
    condition_category = models.ForeignKey(
        Condition_categories, on_delete=models.CASCADE, related_name="conditions")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "conditions"
        
    def __str__(self):
        return self.name
    
class Task_conditions(models.Model):
    task = models.ForeignKey(
        Tasks, on_delete=models.CASCADE, related_name="task_conditions")
    condition = models.ForeignKey(
        Conditions, on_delete=models.CASCADE, related_name="task_conditions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "task_conditions"
        
    def __str__(self):
        return f"{self.task.name} - {self.condition.name}"   
    
class Condition_sets(models.Model):
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="condition_sets")
    name = models.CharField(max_length=100)
    set_type = models.IntegerField(default=0)    # 0:自動表示, 1:保存
    use_count = models.IntegerField(default=0)   # 検索で使用された回数
    last_use_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "condition_sets"
        
    def __str__(self):
        return self.name  
    
class Condition_set_items(models.Model):
    condition_set = models.ForeignKey(
        Condition_sets, on_delete=models.CASCADE, related_name="condition_set_items")
    condition = models.ForeignKey(
        Conditions, on_delete=models.CASCADE, related_name="condition_set_items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "condition_set_items"
        
    def __str__(self):
        return self.name    