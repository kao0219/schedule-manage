from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.contrib.auth.models import User

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

class Family(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return F"Family {self.id}"
    
class Schedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    schedule_title = models.CharField(max_length=100)
    schedule_memo = models.CharField(max_length=255, blank=True)
    image_url = models.ImageField(upload_to='schedule_images/', blank=True, null=True)
    
    COLOR_CHOICES = [
        (1, 'レッド'),
        (2, 'ブルー'),
        (3, 'イエロー'),
        (4, 'グリーン'),
        (5, 'ピンク'),
        (6, 'パープル'),
        (7, 'オレンジ'),
    ]

    color = models.IntegerField(choices=COLOR_CHOICES, blank=True, null=True)

    def get_color_label(self):
        return dict(self.COLOR_CHOICES).get(self.color, '')
    
    REPEAT_CHOICES = [
        (0, 'なし'),
        (1, '毎日'),
        (2, '毎週'),
        (3, '毎月'),
    ]
    repeat_type = models.IntegerField(choices=REPEAT_CHOICES, default=0)
    
    is_all_day = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_title
    
class ScheduleComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, verbose_name='コメントの内容')  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class ScheduleCommentRead(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(ScheduleComment, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')  

    def __str__(self):
        return f"{self.user.email} read {self.comment.id} at {self.read_at}"
    
class Memo(models.Model):
    memo_title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='memo_images/', blank=True, null=True)  # 画像添付
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.memo_title