from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Client
from apps.business_lines.models import BusinessLine


class ClientBusinessLineFilter(admin.SimpleListFilter):
    """Filtro personalizado por línea de negocio jerárquica"""
    title = 'Línea de negocio'
    parameter_name = 'business_line_hierarchy'

    def lookups(self, request, model_admin):
        lines = BusinessLine.objects.filter(is_active=True).order_by('level', 'name')
        choices = []
        for line in lines:
            indent = "    " * (line.level - 1)
            choices.append((line.id, f"{indent}{line.name}"))
        return choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(business_line_id=self.value())
        return queryset


class RenovacionProximaFilter(admin.SimpleListFilter):
    """Filtro para clientes con renovación próxima"""
    title = 'Renovación próxima'
    parameter_name = 'renovacion_proxima'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Próxima (< 30 días)'),
            ('vencida', 'Vencida'),
        )

    def queryset(self, request, queryset):
        from datetime import date, timedelta
        today = date.today()
        
        if self.value() == 'si':
            return queryset.filter(fecha_renovacion__lte=today + timedelta(days=30))
        elif self.value() == 'vencida':
            return queryset.filter(fecha_renovacion__lt=today)
        return queryset


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin para Client con filtros inteligentes y gestión de remanentes
    """
    
    # EDICIÓN DIRECTA EN TABLA - Solo campos que se pueden modificar rápidamente
    list_editable = [
        'precio',
        'metodo_pago', 
        'is_active'
    ]
    
    list_display = [
        'nombre',
        'dni', 
        'get_business_line_path',
        'categoria',
        'precio',  # Editable directamente
        'metodo_pago',  # Editable directamente  
        'fecha_renovacion',
        'get_remanente_display',
        'get_renovacion_status',
        'is_active'  # Editable directamente
    ]
    
    list_filter = [
        'categoria',
        'metodo_pago',
        'is_active',
        ClientBusinessLineFilter,
        RenovacionProximaFilter,
        'business_line__has_remanente'
    ]
    
    search_fields = [
        'nombre', 
        'dni',
        'business_line__name',
        'business_line__parent__name'
    ]
    
    readonly_fields = [
        'remanente_total',
        'dias_hasta_renovacion',
        'created_at', 
        'updated_at'
    ]
    
    # Formulario para AÑADIR/EDITAR clientes (sin valores por defecto automáticos)
    fieldsets = (
        ('✅ Información del Cliente (Obligatorio)', {
            'fields': ('nombre', 'dni', 'business_line'),
            'classes': ('wide',),
            'description': 'Datos básicos requeridos para crear el cliente'
        }),
        ('💰 Configuración del Servicio (Obligatorio)', {
            'fields': ('categoria', 'precio', 'metodo_pago'),
            'classes': ('wide',),
            'description': 'El nutricionista debe seleccionar: White/Black, precio y tarjeta/efectivo'
        }),
        ('📅 Fechas del Servicio (Obligatorio)', {
            'fields': ('fecha_inicio', 'fecha_renovacion'),
            'classes': ('wide',),
            'description': 'El nutricionista debe introducir ambas fechas manualmente'
        }),
        ('💳 Remanentes (Solo si es Black)', {
            'fields': (
                'remanente_pepe', 
                'remanente_pepe_video',
                'remanente_dani', 
                'remanente_aven'
            ),
            'classes': ('collapse',),
            'description': 'Solo completar si el cliente es Black y tiene remanentes pendientes. Se asigna automáticamente según la línea de negocio.'
        }),
        ('📊 Información Calculada Automáticamente', {
            'fields': ('dias_hasta_renovacion', 'remanente_total'),
            'classes': ('collapse',),
            'description': 'Estos campos se calculan automáticamente'
        }),
        ('⚙️ Estado', {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        ('📋 Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # SIN valores por defecto automáticos - el nutricionista introduce todo manualmente
    save_on_top = True  # Botón de guardar arriba y abajo
    list_per_page = 50  # Más clientes por página
    
    ordering = ['business_line__name', 'categoria', 'nombre']
    
    def get_business_line_path(self, obj):
        """Muestra la ruta completa de la línea de negocio"""
        return obj.business_line.get_full_path()
    get_business_line_path.short_description = "Línea de negocio"
    get_business_line_path.admin_order_field = 'business_line__name'
    
    def get_remanente_display(self, obj):
        """Muestra el remanente total con formato"""
        if obj.categoria == 'Black' and obj.remanente_total > 0:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">€{}</span>',
                obj.remanente_total
            )
        elif obj.categoria == 'Black':
            return format_html('<span style="color: #95a5a6;">€0</span>')
        else:
            return format_html('<span style="color: #bdc3c7;">N/A</span>')
    get_remanente_display.short_description = "Remanente"
    
    def get_renovacion_status(self, obj):
        """Muestra el estado de renovación con colores"""
        dias = obj.dias_hasta_renovacion
        if dias is None:
            return format_html('<span style="color: #95a5a6;">N/A</span>')
        elif dias < 0:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">Vencida ({} días)</span>',
                abs(dias)
            )
        elif dias <= 30:
            return format_html(
                '<span style="color: #f39c12; font-weight: bold;">Próxima ({} días)</span>',
                dias
            )
        else:
            return format_html(
                '<span style="color: #27ae60;">{} días</span>',
                dias
            )
    get_renovacion_status.short_description = "Renovación"
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'business_line', 
            'business_line__parent'
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar líneas de negocio activas en el formulario"""
        if db_field.name == "business_line":
            kwargs["queryset"] = BusinessLine.objects.filter(
                is_active=True
            ).select_related('parent').order_by('level', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    actions = ['marcar_como_activo', 'marcar_como_inactivo']
    
    def marcar_como_activo(self, request, queryset):
        """Acción para activar clientes seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} clientes marcados como activos.')
    marcar_como_activo.short_description = "Marcar como activo"
    
    def marcar_como_inactivo(self, request, queryset):
        """Acción para desactivar clientes seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} clientes marcados como inactivos.')
    marcar_como_inactivo.short_description = "Marcar como inactivo"
