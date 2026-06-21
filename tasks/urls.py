from django.urls import path
from . import views

app_name = "tasks"
urlpatterns = [
    path('home/', views.home, name='home'),
    path('task_list/', views.task_list_view, name='task_list'),
    path('add_task/', views.add_task, name='add_task'),
    path('task_detail/<int:task_pk>', views.task_detail_view, name='task_detail'),
    path('edit_task/<int:task_pk>', views.edit_task, name='edit_task'),    
]