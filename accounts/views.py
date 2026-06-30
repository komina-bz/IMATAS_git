from accounts.utils import login_required_custom
from django.shortcuts import render, redirect
from . import forms
from .models import Users
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.contrib import messages

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
    
def password_reset(request):
    return render(request, 'accounts/password_reset.html')

@login_required_custom
def my_account(request):
    user_id = request.session.get("user_id")
    my_account_data = Users.objects.get(id=user_id)
    return render(request, 'accounts/my_account.html', context={
        'my_account_data': my_account_data,
    })

@login_required_custom
def edit_account_name(request):
    user_id = request.session.get("user_id")
    my_account_data = Users.objects.get(id=user_id) 
    edit_name_form = forms.EditNameForm(initial={
        'name': my_account_data.name,
    }) 

    # 保存ボタンを押されたとき
    if request.method == "POST":
        # 既存データ更新
        new_name_form = forms.EditNameForm(request.POST)
        if new_name_form.is_valid():
            new_name = new_name_form.cleaned_data["name"]
            # 変更があった場合 
            if new_name != my_account_data.name:
                my_account_data.name = new_name
                my_account_data.save()
                # 変更しましたの表示
                messages.success(request, f"アカウント名を {new_name} に変更しました")                   
            return redirect('accounts:my_account')
    
    return render(request, 'accounts/edit_account_name.html', {
            "edit_name_form": edit_name_form,
    })

def edit_account_email(request):
    user_id = request.session.get("user_id")
    my_account_data = Users.objects.get(id=user_id) 
    edit_email_form = forms.EditEmailForm(initial={
        'email': my_account_data.email,
    }) 

    # 保存ボタンを押されたとき
    if request.method == "POST":
        # 既存データ更新
        new_email_form = forms.EditEmailForm(request.POST)
        if new_email_form.is_valid():
            new_email = new_email_form.cleaned_data["email"]
            new_email_confirm = new_email_form.cleaned_data["email_confirm"]
            # 変更があった場合 
            if new_email != my_account_data.email:
                # 確認用を一致しなかった場合
                if new_email != new_email_confirm:
                    messages.error(request, "メールアドレスが一致しません")
                    edit_email_form = forms.EditEmailForm(initial={
                        'email': new_email,
                    })                     
                    return render(request, 'accounts/edit_account_email.html', {
                            "edit_email_form": edit_email_form,
                    })
                # 一致した場合
                else:
                    my_account_data.email = new_email
                    my_account_data.save()
                    # 変更しましたの表示
                    messages.success(request, f"メールアドレスを {new_email} に変更しました")                   
                    return redirect('accounts:my_account') 
        else:
            messages.error(request, "メールアドレスの形式が正しくありません")
            return render(request, 'accounts/edit_account_email.html', {
                            "edit_email_form": edit_email_form,
            })
            
    return render(request, 'accounts/edit_account_email.html', {
            "edit_email_form": edit_email_form,
    })

def edit_account_password(request):
    return render(request, 'accounts/edit_account_password.html')

def my_remind(request):
    return render(request, 'accounts/my_remind.html')

def my_conditions(request):
    return render(request, 'accounts/my_conditions.html')

def my_condition_sets(request):
    return render(request, 'accounts/my_condition_sets.html')