from django.contrib import admin
from .models import PlateProject

@admin.register(PlateProject)
class PlateProjectAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'projeto', 'total_amostras', 'email', 'created_at')
    list_filter = ('empresa', 'created_at')
    search_fields = ('empresa', 'projeto', 'email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        """Torna os campos do projeto imutáveis após a criação para preservar integridade"""
        if obj:  # Editando um objeto existente
            return self.readonly_fields + ('empresa', 'projeto', 'total_amostras')
        return self.readonly_fields