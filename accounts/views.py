from django.shortcuts import render
#from .forms import UserForm
from . import forms

def login_view(request):
    return render(request, 'accounts/login.html')

def regist(request):
    user_form = forms.UserForm(request.POST or None)
    return render(request, 'accounts/registration.html', context={
        'user_form': user_form,
    })