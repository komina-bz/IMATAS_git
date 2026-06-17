from django.shortcuts import render
from .forms import UserForm

def login_view(request):
    return render(request, 'accounts/login.html')

def regist(request):
    user_form = UserForm(request.POST or None)
    return render(request, 'accounts/registration.html', context={
        'user_form': user_form,
    })