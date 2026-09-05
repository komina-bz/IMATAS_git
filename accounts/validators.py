from django.core.exceptions import ValidationError


class StrongPasswordValidator:

    def validate(self, password, user=None):

        if not any(c.islower() for c in password):
            raise ValidationError("小文字を含めてください。")

        if not any(c.isupper() for c in password):
            raise ValidationError("大文字を含めてください。")

        if not any(c.isdigit() for c in password):
            raise ValidationError("数字を含めてください。")

    def get_help_text(self):
        return "パスワードには小文字、大文字、数字を含めてください。"