from django import forms
from .models import Users

class UserForm(forms.ModelForm):
    password_confirm = forms.CharField(label='パスワード(確認用)', 
                                       widget=forms.PasswordInput
                                       )   
    class Meta:
        model = Users
        fields = ['name', 'email', 'password']
        labels = {
            'name': 'アカウント名',
            'email': 'メールアドレス',
            'password': 'パスワード',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス", max_length=255)
    password = forms.CharField(
        label="パスワード", max_length=50, widget=forms.PasswordInput
    )

class EditNameForm(forms.Form):
    name = forms.EmailField(label="アカウント名", max_length=100)

class EditEmailForm(forms.Form):
    email = forms.EmailField(label="メールアドレス", max_length=255)
    email_confirm = forms.CharField(label='メールアドレス(確認用)') 


class EditPasswordForm(forms.Form):
    password_current = forms.CharField(
        label="現在のパスワード", widget=forms.PasswordInput
    )
    password = forms.CharField(
        label="新しいパスワード", max_length=50, widget=forms.PasswordInput
    )
    password_confirm = forms.CharField(
        label="新しいパスワード(確認用)", widget=forms.PasswordInput
    )
