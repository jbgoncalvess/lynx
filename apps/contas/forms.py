from django import forms


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu nome de usuário', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite sua senha', 'class': 'form-control'})
    )
