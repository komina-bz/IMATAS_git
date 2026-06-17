from django import forms
#from .models import users

# class UserForm(forms.ModelForm):
    
#     class Meta():
#         model = users
#         fields = ('username', 'email', 'password')

class UserForm(forms.Form):
    
    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField()