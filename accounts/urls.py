from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('regist/', views.regist, name='regist'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('my_account/', views.my_account, name='my_account'),
    path('my_remind/', views.my_remind, name='my_remind'),
    path('my_conditions/', views.my_conditions, name='my_conditions'),
    path('my_condition_sets/', views.my_condition_sets, name='my_condition_sets'),
]