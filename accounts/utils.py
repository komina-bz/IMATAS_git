from django.shortcuts import redirect
from .models import Users

def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("accounts:login")

        # ★ここが重要：request.user に Users インスタンスをセット
        request.user = Users.objects.get(id=user_id)

        return view_func(request, *args, **kwargs)
    return wrapper