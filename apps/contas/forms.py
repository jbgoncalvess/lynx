from django import forms
from django.contrib.auth.models import User


class Registro(forms.ModelForm):
    # Digitar as duas senhas
    password1 = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirme a Senha")

    # Como é alocado os dados do usuário
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    # Verificar se as duas senhas estão iguais
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não correspondem")
        return password2

    # Salvar
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
