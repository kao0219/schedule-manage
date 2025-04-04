from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

#ユーザーの管理用のマネージャー
class CustomUserManager(BaseUserManager):
    def create_user(self, emali, password=None, username=None):
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, username=None):
        user = self.create_user(email=email, passord=password, username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user