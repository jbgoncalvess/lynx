from django.contrib import admin
from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')  # Campos a serem exibidos
    search_fields = ('username',)  # Campos pesquisáveis
    list_filter = ('is_active',)  # Filtros disponíveis

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Permite que apenas usuários superusuários vejam usuários inativos
        if not request.user.is_superuser:
            queryset = queryset.filter(is_active=True)
        return queryset


# Registra o modelo User com a configuração personalizada
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
