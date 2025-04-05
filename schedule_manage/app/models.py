from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

#ユーザーの管理用のマネージャー
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None):
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, username=None):
        user = self.create_user(email=email, password=password, username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


