from django.urls import path
from . import views

app_name = "tasks"
urlpatterns = [
    path('home/', views.home, name='home'),
    path('task_list/', views.task_list, name='task_list'),
    path('add_task/', views.add_task, name='add_task'),
]