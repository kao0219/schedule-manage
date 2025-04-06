from django import forms
from django.contrib.auth.forms import PasswordChangeForm


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