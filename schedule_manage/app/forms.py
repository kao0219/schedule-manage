from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Schedule, COLOR_LABELS
from .models import ScheduleComment 
from .models import Memo


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
        fields = [
            'schedule_title',
            'schedule_memo',
            'is_all_day',
            'start_time',
            'end_time',
            'repeat_type',
            'color',
            'image_url',
        ]

    repeat_type = forms.TypedChoiceField(
        choices=Schedule.REPEAT_CHOICES,
        coerce=int,  # 選択値を int に変換
        widget=forms.RadioSelect,
        label='繰り返し設定',
        initial='0'
    )

    color = forms.TypedChoiceField(
        choices=[(k, v) for k, v in COLOR_LABELS.items()],
        coerce=int,
        label='好きな色を選択'
    )
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = ScheduleComment
        fields = ['content']

def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        # repeat_type の初期値を 0 に設定（デフォルト「なし」にチェック）
        if not self.initial.get('repeat_type'):
            self.initial['repeat_type'] = 0

class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['memo_title', 'content', 'image']