# ==============================================================================
# 1. IMPORTACIONES
# ==============================================================================
from django import forms  # Herramientas de Django para crear formularios.
from .models import Product  # Importamos el modelo Product para vincular el formulario.

# ==============================================================================
# 2. EXTENSIÓN PARA MÚLTIPLES ARCHIVOS (LÓGICA PERSONALIZADA)
# ==============================================================================

# Clase para permitir que el widget de selección de archivos acepte más de uno.
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Habilita la selección múltiple en el navegador.

# Campo personalizado que procesa una lista de imágenes en lugar de solo una.
class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        # Establece nuestro widget personalizado por defecto.
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Limpia y valida cada archivo por separado si se suben varios.
        """
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            # Si hay varios archivos, los valida uno por uno.
            result = [single_file_clean(d, initial) for d in data]
        else:
            # Si solo hay uno, usa la validación estándar.
            result = single_file_clean(data, initial)
        return result

# ==============================================================================
# 3. FORMULARIO PRINCIPAL DE PRODUCTO
# ==============================================================================
class ProductForm(forms.ModelForm):
    
    # Definimos el campo 'extra_imgs' de forma manual para usar la subida múltiple.
    extra_imgs = MultipleFileField(
        required=False, 
        label="Fotos adicionales (Máx 5)",
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'multiple': True,        # Permite seleccionar varios archivos a la vez.
            'id': 'real-input-extra'  # ID útil para manipularlo con JavaScript.
        })
    )

    class Meta:
        # Vinculamos este formulario con el modelo Product.
        model = Product
        
        # Lista de campos del modelo que queremos mostrar en el formulario web.
        fields = [
            'nombre', 'descripcion', 'precio', 'stock', 
            'categoria', 'imagen_principal', 'email_contacto', 'telefono_contacto'
        ]
        
        # Personalización de los campos (Widgets): Agregamos clases de Bootstrap (form-control).
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Monitor Gamer 24"'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe el estado del producto...'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}), # Menú desplegable.
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}), # Campo de foto única.
            'email_contacto': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }