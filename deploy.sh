#!/bin/bash

# Script para implantação do aplicativo Django em produção
# Execute este script como usuário com permissões sudo

# Cores para formatação do output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando implantação da aplicação Gerador de Templates de Placas${NC}"

# 1. Criar ambiente virtual e instalar dependências
echo -e "${GREEN}Criando ambiente virtual e instalando dependências...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Configurações do ambiente
echo -e "${GREEN}Configurando variáveis de ambiente...${NC}"
# Em produção, você deve criar um arquivo .env com suas configurações
# ou definir as variáveis de ambiente diretamente

# 3. Configurações do Django
echo -e "${GREEN}Aplicando migrações do banco de dados...${NC}"
python manage.py migrate
echo -e "${GREEN}Coletando arquivos estáticos...${NC}"
python manage.py collectstatic --noinput

# 4. Criar arquivo do Gunicorn
echo -e "${GREEN}Configurando Gunicorn...${NC}"
cat > gunicorn_config.py << EOF
bind = "0.0.0.0:8181"
workers = 3
timeout = 120
accesslog = "logs/access.log"
errorlog = "logs/error.log"
EOF

# 5. Criar diretório para logs
mkdir -p logs

# 6. Criar serviço systemd para o Gunicorn
echo -e "${GREEN}Criando serviço systemd para o Gunicorn...${NC}"
cat > plate_generator.service << EOF
[Unit]
Description=Gunicorn service for Plate Generator Django Application
After=network.target

[Service]
User=${USER}
Group=${USER}
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/gunicorn -c gunicorn_config.py plate_generator.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 7. Instalar e ativar o serviço systemd
echo -e "${GREEN}Instalando e ativando o serviço...${NC}"
sudo mv plate_generator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable plate_generator.service
sudo systemctl start plate_generator.service

# 8. Configurar Nginx (você deve ter o nginx instalado)
echo -e "${GREEN}Configurando Nginx...${NC}"
cat > plate_generator_nginx << EOF
server {
    listen 8181;
    server_name 92.112.184.107;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $(pwd);
    }

    location /media/ {
        root $(pwd);
    }

    location / {
        include proxy_params;
        proxy_pass http://localhost:8181;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo mv plate_generator_nginx /etc/nginx/sites-available/plate_generator_8181
sudo ln -s /etc/nginx/sites-available/plate_generator_8181 /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Abrir a porta 8181 no firewall (se estiver usando ufw)
sudo ufw allow 8181

echo -e "${GREEN}Implantação concluída com sucesso!${NC}"
echo -e "${YELLOW}A aplicação está sendo executada em: http://92.112.184.107:8181/${NC}"

# Exibe status do serviço
sudo systemctl status plate_generator.service