from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('regist/', views.regist, name='regist'),
    path('password_reset/', views.password_reset, name='password_reset'),
]