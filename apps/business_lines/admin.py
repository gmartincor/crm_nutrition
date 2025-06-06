from django.contrib import admin
from .models import BusinessLine


@admin.register(BusinessLine)
class BusinessLineAdmin(admin.ModelAdmin):
    """
    Admin para BusinessLine con vista jerárquica optimizada
    """
    
    list_display = [
        'get_hierarchy_display', 
        'level', 
        'has_remanente', 
        'remanente_field',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'level',
        'has_remanente', 
        'is_active',
        'parent'
    ]
    
    search_fields = ['name', 'slug']
    
    readonly_fields = ['slug', 'level', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'parent', 'level')
        }),
        ('Configuración de Remanentes', {
            'fields': ('has_remanente', 'remanente_field'),
            'description': 'Configurar si esta línea maneja remanentes para clientes Black'
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['level', 'name']
    
    def get_hierarchy_display(self, obj):
        """Muestra la jerarquía completa con indentación visual"""
        indent = "    " * (obj.level - 1)
        if obj.level == 1:
            icon = "🏛️"
        elif obj.level == 2:
            icon = "📂"
        elif obj.level == 3:
            icon = "📄"
        else:
            icon = "📌"
        
        return f"{indent}{icon} {obj.name}"
    
    get_hierarchy_display.short_description = "Línea de Negocio"
    get_hierarchy_display.admin_order_field = 'name'
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('parent')
    
    class Media:
        css = {
            'all': ('admin/css/business_lines.css',)
        }
        js = ('admin/js/business_lines.js',)
