import os
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from io import BytesIO

from .utils.generator import PlateTemplateGenerator
from .models import PlateProject

class PlateService:
    @staticmethod
    def generate_pdf_for_project(project):
        """
        Gera um arquivo PDF para o projeto fornecido
        
        Args:
            project: Instância do modelo PlateProject
            
        Returns:
            Caminho para o arquivo PDF gerado
        """
        # Configurar dados do projeto para o gerador
        project_data = {
            'empresa': project.empresa,
            'projeto': project.projeto,
            'total_amostras': project.total_amostras
        }
        
        # Gerar código de envio
        cod_envio = project.get_cod_envio()
        
        # Criar gerador de templates
        generator = PlateTemplateGenerator()
        
        # Criar um buffer em memória para o PDF
        buffer = BytesIO()
        
        # Gerar o PDF no buffer
        generator.generate_pdf(buffer, project_data, cod_envio)
        
        # Resetar o ponteiro do buffer para o início
        buffer.seek(0)
        
        # Nome do arquivo PDF
        filename = f"{project.empresa}-{project.projeto}-{cod_envio}.pdf"
        
        # Salvar o PDF no campo do modelo
        project.pdf_file.save(filename, ContentFile(buffer.getvalue()), save=True)
        
        return project.pdf_file.path, filename, cod_envio
    
    @staticmethod
    def send_pdf_by_email(project, pdf_path, filename, cod_envio):
        """
        Envia o PDF gerado por email para o destinatário especificado no projeto
        
        Args:
            project: Instância do modelo PlateProject
            pdf_path: Caminho para o arquivo PDF
            filename: Nome do arquivo PDF
            cod_envio: Código de envio gerado
        
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
        try:
            # Preparar o assunto e o corpo do email
            subject = f'Template de Placas - {project.empresa}-{project.projeto}'
            
            # Contexto para o template de email
            context = {
                'empresa': project.empresa,
                'projeto': project.projeto,
                'total_amostras': project.total_amostras,
                'cod_envio': cod_envio
            }
            
            # Renderizar o corpo do email a partir de um template
            email_body = f"""
            Olá,

            Seu template de placas foi gerado com sucesso.

            Detalhes:
            - Empresa: {project.empresa}
            - Projeto: {project.projeto}
            - Total de Amostras: {project.total_amostras}
            - Código de Envio: {cod_envio}

            O arquivo PDF está anexado a este email.

            Atenciosamente,
            Equipe de Geração de Templates de Placas
            """
            
            # Criar o objeto EmailMessage
            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[project.email]
            )
            
            # Anexar o PDF ao email
            with open(pdf_path, 'rb') as f:
                email.attach(filename, f.read(), 'application/pdf')
            
            # Enviar o email
            email.send(fail_silently=False)
            
            return True
        
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False