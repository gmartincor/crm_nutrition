from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from apps.business_lines.models import BusinessLine


class Client(models.Model):
    """
    Modelo para gestionar clientes y sus ingresos.
    Cada cliente pertenece a una línea de negocio específica.
    """
    
    CATEGORIA_CHOICES = [
        ('White', 'White'),
        ('Black', 'Black'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta'),
        ('efectivo', 'Efectivo'),
    ]
    
    # Datos básicos del cliente
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre completo"
    )
    
    dni = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{8}[A-Za-z]$',
                message='DNI debe tener formato: 12345678A'
            )
        ],
        verbose_name="DNI"
    )
    
    # Relación con línea de negocio
    business_line = models.ForeignKey(
        BusinessLine,
        on_delete=models.PROTECT,
        related_name='clients',
        verbose_name="Línea de negocio",
        help_text="Línea específica: PEPE-normal, Dani-Rubi, etc."
    )
    
    # Categoría y método de pago
    categoria = models.CharField(
        max_length=10,
        choices=CATEGORIA_CHOICES,
        verbose_name="Categoría"
    )
    
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        verbose_name="Método de pago"
    )
    
    # Fechas importantes
    fecha_inicio = models.DateField(
        verbose_name="Fecha de inicio"
    )
    
    fecha_renovacion = models.DateField(
        verbose_name="Fecha de renovación"
    )
    
    # Precio del servicio
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio €"
    )
    
    # Remanentes específicos (solo para Black en líneas correspondientes)
    remanente_pepe = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Remanente PEPE",
        help_text="Solo para PEPE-normal Black"
    )
    
    remanente_pepe_video = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Remanente PEPE Video",
        help_text="Solo para PEPE-videoCall Black"
    )
    
    remanente_dani = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Remanente Dani",
        help_text="Solo para Dani-Rubi Black"
    )
    
    remanente_aven = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Remanente Aven",
        help_text="Solo para Dani Black"
    )
    
    # Control de estado
    is_active = models.BooleanField(
        default=True,
        verbose_name="Cliente activo"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['business_line__name', 'categoria', 'nombre']
        unique_together = ['dni', 'business_line']
    
    def __str__(self):
        return f"{self.nombre} ({self.business_line.get_full_path()} - {self.categoria})"
    
    def clean(self):
        """Validaciones específicas de negocio"""
        super().clean()
        
        # Validar que solo las líneas correctas tengan remanentes
        if self.categoria == 'Black':
            business_line_name = self.business_line.name
            
            # Limpiar remanentes que no corresponden a esta línea
            if business_line_name != 'PEPE-normal':
                self.remanente_pepe = None
            if business_line_name != 'PEPE-videoCall':
                self.remanente_pepe_video = None
            if business_line_name != 'Dani-Rubi':
                self.remanente_dani = None
            if business_line_name != 'Dani':
                self.remanente_aven = None
        else:
            # Clientes White no tienen remanentes
            self.remanente_pepe = None
            self.remanente_pepe_video = None
            self.remanente_dani = None
            self.remanente_aven = None
    
    @property
    def remanente_total(self):
        """Calcula el remanente total del cliente"""
        total = 0
        if self.remanente_pepe:
            total += self.remanente_pepe
        if self.remanente_pepe_video:
            total += self.remanente_pepe_video
        if self.remanente_dani:
            total += self.remanente_dani
        if self.remanente_aven:
            total += self.remanente_aven
        return total
    
    @property
    def dias_hasta_renovacion(self):
        """Calcula días hasta la renovación"""
        if self.fecha_renovacion:
            delta = self.fecha_renovacion - date.today()
            return delta.days
        return None
    
    @property
    def renovacion_proxima(self):
        """True si la renovación es en menos de 30 días"""
        dias = self.dias_hasta_renovacion
        return dias is not None and dias <= 30
    
    def get_remanente_field_name(self):
        """Retorna el nombre del campo de remanente correspondiente"""
        if self.categoria != 'Black':
            return None
            
        business_line_name = self.business_line.name
        remanente_map = {
            'PEPE-normal': 'remanente_pepe',
            'PEPE-videoCall': 'remanente_pepe_video',
            'Dani-Rubi': 'remanente_dani',
            'Dani': 'remanente_aven',
        }
        return remanente_map.get(business_line_name)
