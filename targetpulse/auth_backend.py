from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"EmailBackend: Попытка аутентификации с email: {email}")  # Для отладки
        try:
            user = User.objects.get(email__iexact=email)  # Игнорируем регистр
            if user.check_password(password):
                print(f"EmailBackend: Пароль верный для пользователя {user.username}")  # Для отладки
                return user
            else:
                print("EmailBackend: Неверный пароль.")  # Для отладки
        except User.DoesNotExist:
            print("EmailBackend: Пользователь с таким email не найден.")  # Для отладки
            return None
        except User.MultipleObjectsReturned:
            print("EmailBackend: Найдено несколько пользователей с таким email.")  # Для отладки
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None