from django import forms
from .models import Product

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProductForm(forms.ModelForm):
    # En tu ProductForm...
    extra_imgs = MultipleFileField(
        required=False, 
        label="Fotos adicionales (Máx 5)",
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'multiple': True,  # <--- AGREGA ESTO AQUÍ
            'id': 'real-input-extra' # <--- AGREGA ESTO PARA FACILITAR EL JS
        })
    )

    class Meta:
        model = Product
        # 1. AGREGAMOS 'categoria' a la lista
        fields = [
            'nombre', 'descripcion', 'precio', 'stock', 
            'categoria', 'imagen_principal', 'email_contacto', 'telefono_contacto'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Monitor Gamer 24"'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe el estado del producto...'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            # 2. AGREGAMOS el widget para la categoría
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            # 3. AGREGAMOS el widget para la imagen principal
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'email_contacto': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }