from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Schedule


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].label = '現在のパスワード'
        self.fields['new_password1'].label = '新しいパスワード'
        self.fields['new_password2'].label = 'パスワード再入力'

        for field in self.fields.values():
            field.help_text =''


class CustomEmailChangeForm(forms.Form):
    current_email = forms.EmailField(label='現在のメールアドレス')
    new_email = forms.EmailField(label='新しいメールアドレス')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_email(self):
        current_email = self.cleaned_data['current_email']
        if self.user and current_email !=self.user.email:
            raise forms.ValidationError('')
        return current_email
    
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = (
            'schedule_title',
            'schedule_memo',
            'image_url',
            'color',
            'start_time',
            'end_time',
            'is_all_day',
            'repeat_type',
        )
        
