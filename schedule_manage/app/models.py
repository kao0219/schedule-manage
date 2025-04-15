from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings

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
    family = models.ForeignKey('Family', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    last_login = models.DateTimeField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser

class Invite(models.Model):
    family = models.ForeignKey('Family', on_delete=models.CASCADE, null=True, blank=True)
    invite_token = models.CharField(max_length=255, unique=True, editable=False)
    status = models.IntegerField(default=1) # 1:使用済み 2:未使用
    expires_at = models.DateTimeField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at =models.DateTimeField(auto_now=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

class Family(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return F"Family {self.id}"
    
class Schedule(models.Model):
    schedule_title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Memo(models.Model):
    memo_title = models.CharField(max_length=100)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title