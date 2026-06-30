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

class EditNameForm(forms.ModelForm): 
    class Meta:
        model = Users
        fields = ['name']
        labels = {
            'name': 'アカウント名',
        }

class EditEmailForm(forms.ModelForm): 
    email_confirm = forms.CharField(label='メールアドレス(確認用)') 
    class Meta:
        model = Users
        fields = ['email']
        labels = {
            'email': 'メールアドレス',
        }
