from django.urls import path
from . import views

app_name = "tasks"
urlpatterns = [
    path('home/', views.home, name='home'),
    path('imatas_result/', views.imatas_result, name='imatas_result'),
    path('task_list/', views.task_list, name='task_list'),
    path('incomplete_task_list/', views.incomplete_task_list, name='incomplete_task_list'),
    path('task_list_by_due/', views.task_list_by_due, name='task_list_by_due'),
    path('add_task/', views.update_task, name='add_task'),
    path('edit_task/<int:task_pk>', views.update_task, name='edit_task'), 
    path('task_detail/<int:task_pk>', views.task_detail_view, name='task_detail'),
    path('delete_task/<int:task_pk>', views.delete_task, name='delete_task'),    
]