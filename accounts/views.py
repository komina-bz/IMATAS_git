from django.shortcuts import render
#from .forms import UserForm
from . import forms
from .models import Users

def login_view(request):
    return render(request, 'accounts/login.html')

def regist(request):
    user_form = forms.UserForm(request.POST or None)
    if request.method == 'POST':
        user_form = forms.UserForm(request.POST or None)
        if user_form.is_valid():
            name = user_form.cleaned_data['name']
            email = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password']
            user = Users(
                name=name, email=email, password=password,
                
            )
            user.save()
    
    return render(request, 'accounts/registration.html', context={
        'user_form': user_form,
    })