from django import forms
from django.core.validators import RegexValidator
from .models import PlateProject

class PlateProjectForm(forms.ModelForm):
    """Formulário para solicitação de geração de templates de placas"""
    
    # Validadores personalizados
    empresa_validator = RegexValidator(
        regex=r'^\d{3}$',
        message="O código da empresa deve conter exatamente 3 dígitos numéricos"
    )
    
    # Campos com validação customizada
    empresa = forms.CharField(
        max_length=3, 
        validators=[empresa_validator],
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 001'})
    )
    
    projeto = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: PROJ123ABC'})
    )
    
    class Meta:
        model = PlateProject
        fields = ['empresa', 'projeto', 'total_amostras', 'email']
        widgets = {
            'total_amostras': forms.NumberInput(attrs={
                'min': 90, 
                'max': 40000,
                'placeholder': 'Entre 90 e 40000'
            }),
            'email': forms.EmailInput(attrs={'placeholder': 'seu@email.com'})
        }
    
    def clean(self):
        """Validação adicional de formulário"""
        cleaned_data = super().clean()
        
        # Verifica se já existe um projeto com a mesma combinação empresa+projeto
        empresa = cleaned_data.get('empresa')
        projeto = cleaned_data.get('projeto')
        
        if empresa and projeto:
            if PlateProject.objects.filter(empresa=empresa, projeto=projeto).exists():
                raise forms.ValidationError(
                    "Já existe um projeto cadastrado com esta combinação de empresa e projeto."
                )
        
        return cleaned_data