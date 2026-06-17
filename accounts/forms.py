from django import forms
#from .models import users

# class UserForm(forms.ModelForm):
    
#     class Meta():
#         model = users
#         fields = ('username', 'email', 'password')

class UserForm(forms.Form):
    
    name = forms.CharField(label='アカウント名')
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード')
    password2 = forms.CharField(label='パスワード(確認用)')