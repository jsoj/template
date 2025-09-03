from django.core.mail import send_mail

send_mail(
    'Teste de Email do Django',
    'Este é um e-mail de teste enviado do Django usando o servidor Postfix.',
    'noreplay@jsoj.site',
    ['contato@agromarkers.com.br'],  # Use um email externo como destinatário
    fail_silently=False,
)
