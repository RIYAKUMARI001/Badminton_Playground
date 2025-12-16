from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Coach, Court, Equipment


class AvailabilitySearchForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))


class BookingForm(forms.Form):
    customer_name = forms.CharField(max_length=100)
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    court = forms.ModelChoiceField(queryset=Court.objects.filter(is_active=True))
    coach = forms.ModelChoiceField(queryset=Coach.objects.filter(is_active=True), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for equipment in Equipment.objects.filter(is_active=True):
            self.fields[f"equipment_{equipment.id}"] = forms.IntegerField(
                label=f"{equipment.name} quantity",
                min_value=0,
                required=False,
                initial=0,
            )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
        })
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. jane_doe",
        })
    )
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password",
        })
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password",
        })
    )
    
    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


