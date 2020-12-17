from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


# https://stackoverflow.com/a/37332393/8538597
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            if username:
                user = UserModel.objects.get(email=username)
            else:
                user = UserModel.objects.get(email=kwargs["email"])
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None