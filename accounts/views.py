from accounts.utils import login_required_custom
from django.shortcuts import render, redirect
from . import forms
from .models import Users
from tasks.models import Conditions, Condition_categories
from tasks.forms import ConditionForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponse

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

@login_required_custom
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

@login_required_custom
def edit_account_password(request):
    user_id = request.session.get("user_id")
    my_account_data = Users.objects.get(id=user_id) 
    edit_password_form = forms.EditPasswordForm(request.POST or None)

    # 保存ボタンを押されたとき
    if request.method == "POST":
        password_current = request.POST.get("password_current")
        new_password = request.POST.get("password")
        new_password_confirm = request.POST.get("password_confirm")

        # 現在のパスワードが間違えている場合
        if not check_password(password_current, my_account_data.password):
            messages.error(request, "現在のパスワードが一致しません")
            return render(request, 'accounts/edit_account_password.html', {
                "edit_password_form": edit_password_form,
                })
        # 新しいパスワードと確認用が一致しない場合
        if new_password != new_password_confirm:
            messages.error(request, "新しいパスワードが一致しません")
            return render(request, 'accounts/edit_account_password.html', {
                "edit_password_form": edit_password_form,
                })
        # password強度チェック
        try:
            validate_password(new_password)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return render(request, "accounts/edit_account_password.html", context={
                "edit_password_form": edit_password_form,
            })  
         
        # エラーが無ければ変更    
        if edit_password_form.is_valid():
            # 変更があった場合 
            if new_password != my_account_data.password:
                my_account_data.password = make_password(new_password)   # ハッシュ化
                my_account_data.save()
                # 変更しましたの表示
                messages.success(request, f"パスワードを変更しました")                   
                return redirect('accounts:my_account') 
            
    return render(request, 'accounts/edit_account_password.html', {
            "edit_password_form": edit_password_form,
    })    

@login_required_custom
def my_remind(request):
    user_id = request.session.get("user_id")
    my_account_data = Users.objects.get(id=user_id)
    
    # 通知ありの場合、通知タイミングに初期値を渡す
    if my_account_data.remind_enabled == 1:
        return render(request, 'accounts/my_remind.html', {
                "my_account_data": my_account_data,
                "default_remind_day": my_account_data.remind_before_days,
                "default_remind_time": my_account_data.remind_time,
        })      
            
    return render(request, 'accounts/my_remind.html', {
            "my_account_data": my_account_data,
    })

# 通知設定のボタンが押下されたときの処理
@login_required_custom    
def button_clicked(request):
    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.session.get("user_id")
        my_account_data = Users.objects.get(id=user_id)

        # 期限通知を受け取るON/OFFを切り替える
        if action == "remind_enabled_btn":
            if my_account_data.remind_enabled == 0:
                my_account_data.remind_enabled = 1
            else:
                my_account_data.remind_enabled = 0
            my_account_data.save()
            return redirect("accounts:my_remind")

        # 通知タイミングを保存する
        elif action == "remind_timing_set_btn":
            # 通知タイミング（〇日前）を設定
            selected_list = request.POST.getlist("option")
            selected_remind_day = selected_list[0]
            if selected_remind_day == '当日':
                my_account_data.remind_before_days = 0
            elif selected_remind_day == '1日前':
                my_account_data.remind_before_days = 1
            elif selected_remind_day == '3日前':
                my_account_data.remind_before_days = 3
            elif selected_remind_day == '7日前':
                my_account_data.remind_before_days = 7
                
            # 通知する時間帯を取得
            selected_remind_time = request.POST.get("remind_time")
            my_account_data.remind_time = selected_remind_time
            
            # 保存
            my_account_data.save()
            return redirect("accounts:my_remind")

    return HttpResponse("")

@login_required_custom 
def my_conditions(request):
    user_id = request.session.get("user_id")
    add_condition_form = ConditionForm() 
    
    # カテゴリー毎に状況をまとめる
    action_conditions = Conditions.objects.filter(
        user_id = user_id, 
        condition_category_id = 1)
    place_conditions = Conditions.objects.filter(
        user_id = user_id, 
        condition_category_id = 2)
    time_conditions = Conditions.objects.filter(
        user_id = user_id, 
        condition_category_id = 3)
    others_conditions = Conditions.objects.filter(
        user_id = user_id, 
        condition_category_id = 4)
    
    # 追加か編集ボタンが押された場合
    if request.method == "POST":
        condition_id = request.POST.get("condition_id")
        condition_name = request.POST.get("name")
        
        # 編集ボタンが押された場合
        if condition_id:
            edit_condition = Conditions.objects.get(id=condition_id)
            edit_condition.name = condition_name
            edit_condition.save()
        
        # 追加ボタンが押された場合    
        else:
            new_condition_form = ConditionForm(request.POST) 
            if new_condition_form.is_valid():
                new_condition = new_condition_form.save(commit=False)
                item_category = request.POST.get("type") 
                if item_category == "action":
                    new_condition.condition_category_id = 1 # 行動
                elif item_category == "place":
                    new_condition.condition_category_id = 2 # 場所
                elif item_category == "time":
                    new_condition.condition_category_id = 3 # 時間
                else:
                    new_condition.condition_category_id = 4 # その他
                new_condition.user_id = user_id
                new_condition.name = condition_name
                new_condition.save()
                
        return redirect('accounts:my_conditions')
        
    return render(request, 'accounts/my_conditions.html', {
            "add_condition_form": add_condition_form,
            "action_conditions": action_conditions,
            "place_conditions": place_conditions,
            "time_conditions": time_conditions,
            "others_conditions": others_conditions,
    })

def my_condition_sets(request):
    return render(request, 'accounts/my_condition_sets.html')