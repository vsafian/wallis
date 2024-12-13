from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, SetPasswordMixin
from .models import Worker

class WorkerCreateForm(UserCreationForm):
    class Meta:
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "phone_number",
            "workplace"
        )


class WorkerPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ("phone_number",)
