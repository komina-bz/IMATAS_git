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
            'name': '名前',
            'email': 'メールアドレス',
            'password': 'パスワード',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス")
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput
    )

