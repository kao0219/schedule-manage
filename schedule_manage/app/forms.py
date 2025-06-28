import re
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

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError('パスワードは8文字以上で入力してください。')
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise forms.ValidationError('パスワードには英字と数字の両方を含めてください。')
        return password        


class CustomEmailChangeForm(forms.Form):
    current_email = forms.EmailField(label='現在のメールアドレス')
    new_email = forms.EmailField(label='新しいメールアドレス')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_email(self):
        current_email = self.cleaned_data['current_email']
        if self.user and current_email !=self.user.email:
            raise forms.ValidationError('現在のアドレスが一致しません。')
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
            'schedule_title': forms.TextInput(attrs={'placeholder': 'タイトル',}),
            'schedule_memo': forms.Textarea(attrs={
            'placeholder': 'メモ', 
            'style': 'resize: none;'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ラベルをすべて非表示にする場合
        for field in self.fields.values():
            field.label = ''


    def clean(self):
        
        cleaned_data = super().clean()
        is_all_day = bool(cleaned_data.get('is_all_day'))
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # 開始・終了が未入力のとき
        if not start_time or not end_time:
            self.add_error('end_time', '開始・終了時間を入力してください。')
            return cleaned_data

        # 終日 or 通常どちらでも、開始 > 終了 はバリデーションエラー
        if start_time > end_time:
            self.add_error('end_time', '開始時間より終了時間を後に設定してください。')
        return cleaned_data

    repeat_type = forms.TypedChoiceField(
        choices=Schedule.REPEAT_CHOICES,
        coerce=int,  # 選択値を int に変換
        widget=forms.RadioSelect,
        label='繰り返し設定',
        initial='0',
        required=False #　日跨ぎの予定登録のため追加
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].choices = [('', '好きな色を選択')] + list(self.fields['color'].choices) 


class CommentForm(forms.ModelForm):
    class Meta:
        model = ScheduleComment
        fields = ['content']

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        

def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        # repeat_type の初期値を 0 に設定
        if not self.initial.get('repeat_type'):
            self.initial['repeat_type'] = 0

class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['memo_title', 'content', 'image']
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')  # 現在のメモを保持
        super().__init__(*args, **kwargs)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image and self.instance:
            return self.instance.image  # 画像変更なしなら元の画像をそのまま
        return image