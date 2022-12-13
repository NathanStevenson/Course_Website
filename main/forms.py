from django.forms import ModelForm
from django import forms
from .models import myUser

class UserForm(ModelForm):
    class Meta:
        model = myUser
        fields = ['email', 'major', 'graduationYear', 'summary']

