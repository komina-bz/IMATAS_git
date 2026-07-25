from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('regist/', views.regist, name='regist'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    # path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    # path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    # path(
    #     "password_reset/",
    #     auth_views.PasswordResetView.as_view(
    #         success_url=reverse_lazy("accounts:password_reset_done")
    #     ),
    #     name="password_reset",
    # ),

    # path(
    #     "password_reset/done/",
    #     auth_views.PasswordResetDoneView.as_view(),
    #     name="password_reset_done",
    # ),
    # path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('my_account/', views.my_account, name='my_account'),
    path('my_remind/', views.my_remind, name='my_remind'),
    path("button_clicked/", views.button_clicked, name="button_clicked"),
    path('my_conditions/', views.my_conditions, name='my_conditions'),
    path('my_condition_sets/', views.my_condition_sets, name='my_condition_sets'),
    path('add_condition_set/', views.update_condition_set, name='add_condition_set'),
    path('edit_condition_set/<int:set_pk>', views.update_condition_set, name='edit_condition_set'),
    path('delete_condition_set/<int:set_pk>', views.delete_condition_set, name='delete_condition_set'),        
    path('edit_account_name/', views.edit_account_name, name='edit_account_name'),
    path('edit_account_email/', views.edit_account_email, name='edit_account_email'),
    path('edit_account_password/', views.edit_account_password, name='edit_account_password'),
]