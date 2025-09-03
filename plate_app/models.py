from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os

def pdf_upload_path(instance, filename):
    """Gera um caminho único para salvar os arquivos PDF"""
    ext = filename.split('.')[-1]
    filename = f"{instance.empresa}-{instance.projeto}-{uuid.uuid4().hex}.{ext}"
    return os.path.join('pdfs', filename)

class PlateProject(models.Model):
    """Modelo para armazenar informações do projeto de placas"""
    empresa = models.CharField(max_length=3, verbose_name="Código da Empresa")
    projeto = models.CharField(max_length=10, verbose_name="Código do Projeto")
    total_amostras = models.IntegerField(
        validators=[
            MinValueValidator(90, message="O número mínimo de amostras é 90."),
            MaxValueValidator(40000, message="O número máximo de amostras é 40000.")
        ],
        verbose_name="Total de Amostras"
    )
    email = models.EmailField(verbose_name="Email para Envio")
    pdf_file = models.FileField(upload_to=pdf_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Projeto de Placas"
        verbose_name_plural = "Projetos de Placas"
        unique_together = ('empresa', 'projeto')  # Impede duplicação de empresa+projeto
    
    def __str__(self):
        return f"{self.empresa}-{self.projeto} ({self.total_amostras} amostras)"
    
    def get_cod_envio(self):
        """Gera o código de envio baseado na data de criação"""
        if self.created_at:
            year = str(self.created_at.year)[-2:]
            day_of_year = self.created_at.timetuple().tm_yday
            sequence = str(self.id).zfill(2)
            return f"{year}{day_of_year}{sequence}"
        return "000000"