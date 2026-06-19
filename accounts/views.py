from django.shortcuts import render, redirect
from . import forms
from .models import Users
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError

def login_view(request):
    login_form = forms.LoginForm(request.POST or None)
    if request.method == 'POST':
        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")
        if login_form.is_valid():
            # 一致するemailを検索
            try:
                user = Users.objects.get(email=email)
            except Users.DoesNotExist:
                login_form.add_error(None, "メールアドレスかパスワードが違います")
                return render(request, "accounts/login.html", {"login_form": login_form})

            # passwordが一致するかチェック
            if check_password(password, user.password):
                # ③ セッションに保存（ログイン成功）
                request.session["user_id"] = user.id
                return redirect("tasks:home")
            else:
                login_form.add_error(None, "メールアドレスかパスワードが違います")           
                  
    return render(request, 'accounts/login.html', context={
        'login_form': login_form,
    })
    
#def logout_view(request):
#    logout(request)
#    return redirect('accounts/login.html')

def regist(request):
    user_form = forms.UserForm(request.POST or None)
    if request.method == 'POST':
        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        
        # メールアドレス重複チェック
        if Users.objects.filter(email=email).exists():
            return render(request, "accounts/regist.html", {
                "user_form": user_form,
                "error": "このメールアドレスは既に登録されています"
            })
            
        # password一致チェック
        if password != password_confirm:
            return render(request, "accounts/regist.html", context={
                "user_form": user_form,
                "error": "パスワードが一致しません"
            })                 
        
        # password強度チェック
        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, "accounts/regist.html", context={
                "user_form": user_form,
                "error": e.messages[0]
            })            
        
        # valid → 登録
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.email = email
            user.password = make_password(password)   # ハッシュ化
            user.save()  
            return redirect('accounts:login')

    return render(request, 'accounts/regist.html', context={
        'user_form': user_form,
    })