from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import UserFile

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ChangeUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UploadUserFileForm(ModelForm):
    class Meta:
        model = UserFile
        fields = ['data_file']

def create_choose_features_form(columns:list):
    class ChooseFeaturesForm(forms.Form):
        i = 0
        for col in columns:
            locals()[f'checkbox_{i}'] = forms.BooleanField(label=col, required=False, initial=True)
            i += 1
    return ChooseFeaturesForm