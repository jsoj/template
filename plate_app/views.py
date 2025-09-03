from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, FileResponse
from django.conf import settings

from .forms import PlateProjectForm
from .models import PlateProject
from .services import PlateService
import os

class PlateFormView(FormView):
    template_name = 'plate_app/form.html'
    form_class = PlateProjectForm
    success_url = reverse_lazy('plate_success')
    
    def form_valid(self, form):
        # Salvar o projeto no banco de dados
        project = form.save()
        
        try:
            # Gerar o PDF para o projeto
            pdf_path, filename, cod_envio = PlateService.generate_pdf_for_project(project)
            
            # Enviar o PDF por email
            email_sent = PlateService.send_pdf_by_email(project, pdf_path, filename, cod_envio)
            
            if email_sent:
                # Armazenar os dados na sessão para exibir na página de sucesso
                self.request.session['success_data'] = {
                    'empresa': project.empresa,
                    'projeto': project.projeto,
                    'total_amostras': project.total_amostras,
                    'email': project.email,
                    'cod_envio': cod_envio
                }
                
                return super().form_valid(form)
            else:
                messages.error(
                    self.request, 
                    "O PDF foi gerado, mas houve um problema ao enviar o email. Por favor, tente novamente."
                )
                # Excluir o projeto se o email não pôde ser enviado
                project.delete()
                return self.form_invalid(form)
                
        except Exception as e:
            # Se houver erro na geração do PDF, exibir mensagem e não salvar o projeto
            messages.error(
                self.request, 
                f"Ocorreu um erro ao gerar o PDF: {str(e)}"
            )
            # Excluir o projeto se houve erro na geração do PDF
            project.delete()
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            "Por favor, corrija os erros no formulário."
        )
        return super().form_invalid(form)

def success_view(request):
    # Recuperar os dados da sessão
    success_data = request.session.get('success_data', {})
    
    # Limpar os dados da sessão após uso
    if 'success_data' in request.session:
        del request.session['success_data']
    
    # Se não houver dados de sucesso, redirecionar para o formulário
    if not success_data:
        return redirect('plate_form')
    
    return render(request, 'plate_app/success.html', success_data)

def download_pdf_view(request, cod_envio):
    """
    View para download direto do arquivo PDF gerado
    """
    try:
        # Buscar todos os projetos (limitado a um número razoável)
        all_projects = PlateProject.objects.all().order_by('-created_at')[:50]
        
        # Tentar encontrar o projeto pelo código de envio
        project = None
        for p in all_projects:
            if p.get_cod_envio() == cod_envio:
                project = p
                break
                
        # Se não encontrou, tenta extrair o ID do projeto a partir do código
        if not project and len(cod_envio) >= 2:
            try:
                # Tente usar os últimos dígitos como ID do projeto
                project_id = int(cod_envio[-2:])
                project = PlateProject.objects.filter(id=project_id).first()
            except (ValueError, IndexError):
                pass
        
        # Se ainda não encontrou, tente outras abordagens
        if not project:
            # Logging para diagnóstico
            print(f"Não foi possível encontrar o projeto com código: {cod_envio}")
            print(f"Projetos disponíveis: {[p.id for p in all_projects]}")
            
            messages.error(request, f"Não foi possível encontrar o projeto com código: {cod_envio}")
            return redirect('plate_form')
        
        # Se encontrou o projeto, verifica se o PDF existe
        if not project.pdf_file:
            messages.error(request, "Arquivo PDF não encontrado para este projeto.")
            return redirect('plate_form')
        
        # Verifica se o arquivo físico existe
        if not os.path.exists(project.pdf_file.path):
            messages.error(request, "O arquivo PDF não foi encontrado no servidor.")
            return redirect('plate_form')
        
        # Retorna o arquivo para download
        response = FileResponse(open(project.pdf_file.path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{project.empresa}-{project.projeto}-{cod_envio}.pdf"'
        return response
        
    except Exception as e:
        import traceback
        print(f"Erro ao fazer download do PDF: {e}")
        print(traceback.format_exc())
        
        messages.error(request, f"Ocorreu um erro ao fazer o download do PDF: {str(e)}")
        return redirect('plate_form')



