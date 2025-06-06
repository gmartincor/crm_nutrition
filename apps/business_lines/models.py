from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class BusinessLine(models.Model):
    """
    Modelo para gestionar las líneas de negocio jerárquicas.
    Estructura: Jaen -> PEPE -> PEPE-normal, etc.
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Ej: Jaen, PEPE, PEPE-normal"
    )
    
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="Slug",
        help_text="Se genera automáticamente"
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Línea padre",
        help_text="Para crear jerarquía: Jaen -> PEPE -> PEPE-normal"
    )
    
    level = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Nivel",
        help_text="1=Principal (Jaen), 2=Sublínea (PEPE), 3=Sub-sublínea (PEPE-normal)"
    )
    
    # Configuración de remanentes
    has_remanente = models.BooleanField(
        default=False,
        verbose_name="Tiene remanente",
        help_text="Si esta línea maneja remanentes en categoría Black"
    )
    
    remanente_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Campo de remanente",
        help_text="Campo específico: remanente_pepe, remanente_dani, etc."
    )
    
    # Control de estado
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Línea de Negocio"
        verbose_name_plural = "Líneas de Negocio"
        ordering = ['level', 'name']
        unique_together = ['name', 'parent']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-generar slug si no existe
        if not self.slug:
            base_slug = slugify(self.name)
            if self.parent:
                base_slug = f"{self.parent.slug}-{base_slug}"
            self.slug = base_slug
        
        # Auto-calcular nivel basado en jerarquía
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
            
        super().save(*args, **kwargs)
    
    def clean(self):
        # Validar que no se cree una jerarquía circular
        if self.parent:
            parent = self.parent
            while parent:
                if parent == self:
                    raise ValidationError("No se puede crear una referencia circular")
                parent = parent.parent
        
        # Validar nivel máximo (evitar jerarquías muy profundas)
        if self.level > 4:
            raise ValidationError("No se permiten más de 4 niveles de jerarquía")
    
    def get_full_path(self):
        """Retorna la ruta completa: Jaen > PEPE > PEPE-normal"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " > ".join(path)
    
    def get_descendants(self):
        """Retorna todos los descendientes de esta línea"""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def is_leaf(self):
        """Retorna True si es una línea terminal (sin hijos)"""
        return not self.children.exists()
