from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Schedule
from .models import ScheduleComment 
from .models import Memo
from django.forms.widgets import DateTimeInput
from django.core.exceptions import ValidationError

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
        widgets = {
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        print("[DEBUG] clean() が呼び出された")
        cleaned_data = super().clean()
        is_all_day = bool(cleaned_data.get('is_all_day'))
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        print(f"[DEBUG] start_time: {start_time}, end_time: {end_time}")

        if not is_all_day:
            if not start_time or not end_time:
                # print("エラー：開始または終了時間が未入力")
                raise forms.ValidationError('開始・終了時間を入力してください。')
            
            if start_time >= end_time:
                # print("エラー：開始が終了より後になっている")
                raise forms.ValidationError("開始時間は終了時間より前に設定してください。")
        else:
            print("[DEBUG] 終日チェックされています。")
        return cleaned_data

    repeat_type = forms.TypedChoiceField(
        choices=Schedule.REPEAT_CHOICES,
        coerce=int,  # 選択値を int に変換
        widget=forms.RadioSelect,
        label='繰り返し設定',
        initial='0'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].choices = [('', '好きな色を選択')] + list(self.fields['color'].choices) 



class CommentForm(forms.ModelForm):
    class Meta:
        model = ScheduleComment
        fields = ['content']

def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        # repeat_type の初期値を 0 に設定
        if not self.initial.get('repeat_type'):
            self.initial['repeat_type'] = 0

class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['memo_title', 'content', 'image']