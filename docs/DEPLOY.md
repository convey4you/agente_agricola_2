# Documentação de Deploy - AgroTech Portugal

## Visão Geral

Este documento descreve o processo completo de deploy da plataforma AgroTech Portugal em ambiente de produção, incluindo configuração de infraestrutura, monitoramento e procedimentos operacionais.

## Pré-requisitos

### Infraestrutura Mínima
- **CPU**: 4 cores (recomendado 8 cores)
- **RAM**: 8GB (recomendado 16GB)
- **Disco**: 100GB SSD (recomendado 200GB)
- **Rede**: Conexão estável com IP público
- **SO**: Ubuntu 20.04+ / CentOS 8+ / Docker compatible

### Software Necessário
```bash
# Docker Engine 20.10+
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 2.0+
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git
sudo apt-get update && sudo apt-get install -y git

# Utilitários
sudo apt-get install -y curl wget jq bc htop
```

### Domínio e DNS
- Domínio registrado (ex: agrotech.pt)
- Subdominios configurados:
  - `app.agrotech.pt` → IP do servidor
  - `api.agrotech.pt` → IP do servidor
  - `monitoring.agrotech.pt` → IP do servidor

## Processo de Deploy

### 1. Preparação do Ambiente

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/agrotech-portugal.git
cd agrotech-portugal

# Criar diretórios necessários
mkdir -p logs backups ssl monitoring/data

# Configurar permissões
sudo chown -R $USER:$USER logs backups
chmod +x scripts/*.sh
```

### 2. Configuração de Variáveis

```bash
# Copiar template de produção
cp .env.prod.example .env.prod

# Editar configurações
nano .env.prod
```

**Variáveis críticas a configurar**:
```env
# Base de dados
DATABASE_URL=postgresql://postgres:senha_segura@db:5432/agrotech
DATABASE_PASSWORD=senha_muito_segura

# Aplicação
FLASK_SECRET_KEY=chave_secreta_gerada_com_openssl
JWT_SECRET_KEY=outra_chave_secreta_para_jwt

# APIs externas
OPENWEATHER_API_KEY=sua_chave_openweather

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_USER=seu-email@agrotech.pt
SMTP_PASSWORD=senha-aplicacao

# SSL/Domínio
DOMAIN=agrotech.pt
EMAIL_ADMIN=admin@agrotech.pt
```

### 3. Configuração SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt-get install -y certbot

# Obter certificado
sudo certbot certonly --standalone \
  -d agrotech.pt \
  -d app.agrotech.pt \
  -d api.agrotech.pt \
  -d monitoring.agrotech.pt \
  --email admin@agrotech.pt \
  --agree-tos \
  --non-interactive

# Copiar certificados
sudo cp /etc/letsencrypt/live/agrotech.pt/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/agrotech.pt/privkey.pem ssl/
sudo chown $USER:$USER ssl/*
```

### 4. Deploy da Aplicação

```bash
# Executar script de deploy
./scripts/deploy.sh

# Ou deploy manual
docker-compose -f docker-compose.prod.yml up -d --build

# Verificar status
docker-compose -f docker-compose.prod.yml ps
```

### 5. Configuração Inicial

```bash
# Aguardar serviços iniciarem
sleep 30

# Inicializar base de dados
docker-compose -f docker-compose.prod.yml exec app python -c "
from app import create_app
from app.database import init_db
app = create_app()
with app.app_context():
    init_db()
"

# Criar usuário administrador
docker-compose -f docker-compose.prod.yml exec app python -c "
from app import create_app
from app.models import User
from app.database import db
app = create_app()
with app.app_context():
    admin = User(
        nome='Administrador',
        email='admin@agrotech.pt',
        role='admin'
    )
    admin.set_password('senha_admin_temporaria')
    db.session.add(admin)
    db.session.commit()
    print('Usuário admin criado com sucesso')
"

# Executar health check
./scripts/health-check.sh
```

## Configuração de Monitoramento

### 1. Acesso ao Grafana
```bash
# URL: https://monitoring.agrotech.pt
# Usuário inicial: admin
# Senha inicial: admin

# Alterar senha no primeiro login
```

### 2. Configurar Datasources
1. Acessar Grafana → Configuration → Data Sources
2. Adicionar Prometheus: `http://prometheus:9090`
3. Testar conexão
4. Importar dashboards da pasta `monitoring/grafana/dashboards/`

### 3. Configurar Alertas
```bash
# Verificar configuração de alertas
docker-compose -f docker-compose.prod.yml exec prometheus promtool check config /etc/prometheus/prometheus.yml
docker-compose -f docker-compose.prod.yml exec prometheus promtool check rules /etc/prometheus/alerts.yml

# Configurar webhook para alertas
curl -X POST http://localhost:9093/api/v1/receivers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "webhook",
    "webhook_configs": [{
      "url": "https://api.agrotech.pt/alerts/webhook"
    }]
  }'
```

## Configuração de Backup

### 1. Backup Automático
```bash
# Configurar cron para backup diário às 2h
echo "0 2 * * * /path/to/agrotech-portugal/scripts/backup.sh" | sudo crontab -
```

### 2. Teste de Backup
```bash
# Executar backup manual
./scripts/backup.sh

# Verificar backup criado
ls -la backups/

# Testar restauração (ambiente de teste)
./scripts/restore.sh backups/backup_20240101_020000.tar.gz
```

### 3. Backup para Cloud (Opcional)
```bash
# Instalar AWS CLI ou Google Cloud SDK
# Configurar credenciais
# Adicionar ao script de backup:

# Para AWS S3
aws s3 cp backups/backup_$timestamp.tar.gz s3://agrotech-backups/

# Para Google Cloud Storage
gsutil cp backups/backup_$timestamp.tar.gz gs://agrotech-backups/
```

## Configuração de Domínio e Proxy

### 1. Configuração Nginx
O arquivo `nginx/nginx.conf` já está configurado com:
- SSL/TLS com Let's Encrypt
- Rate limiting
- Headers de segurança
- Proxy para aplicação
- Gzip compression
- Cache estático

### 2. Verificação de Conectividade
```bash
# Testar endpoints principais
curl -I https://agrotech.pt
curl -I https://api.agrotech.pt/health
curl -I https://monitoring.agrotech.pt

# Testar SSL
openssl s_client -connect agrotech.pt:443 -servername agrotech.pt
```

## Operações Pós-Deploy

### 1. Verificação de Saúde
```bash
# Health check completo
./scripts/health-check.sh

# Verificar logs
docker-compose -f docker-compose.prod.yml logs app --tail=50
docker-compose -f docker-compose.prod.yml logs nginx --tail=50

# Verificar métricas
curl http://localhost:9090/metrics
```

### 2. Configuração de Usuários
```bash
# Acessar aplicação
# URL: https://agrotech.pt
# Login: admin@agrotech.pt
# Senha: senha_admin_temporaria

# 1. Alterar senha do admin
# 2. Configurar perfil do administrador
# 3. Criar usuários iniciais
# 4. Configurar culturas e propriedades de teste
```

### 3. Configuração de Integrações
```bash
# Testar API do clima
curl "https://api.openweathermap.org/data/2.5/weather?q=Lisboa&appid=SUA_API_KEY"

# Configurar webhooks se necessário
# Configurar integrações com sistemas externos
```

## Troubleshooting

### Problemas Comuns

#### 1. Aplicação não inicia
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs app

# Verificar variáveis de ambiente
docker-compose -f docker-compose.prod.yml exec app env | grep -E "(DATABASE|FLASK|SECRET)"

# Verificar conectividade com BD
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres
```

#### 2. SSL não funciona
```bash
# Verificar certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew --dry-run

# Verificar configuração Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

#### 3. Base de dados inacessível
```bash
# Verificar status do PostgreSQL
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Verificar logs
docker-compose -f docker-compose.prod.yml logs db

# Conectar manualmente
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d agrotech
```

#### 4. Alta utilização de recursos
```bash
# Monitorar recursos
htop
docker stats

# Verificar logs por vazamentos de memória
docker-compose -f docker-compose.prod.yml logs app | grep -i "memory\|out of memory"

# Reiniciar serviços se necessário
docker-compose -f docker-compose.prod.yml restart app
```

### Logs Importantes

#### Localizações
- **Aplicação**: `docker-compose logs app`
- **Nginx**: `docker-compose logs nginx`
- **PostgreSQL**: `docker-compose logs db`
- **Redis**: `docker-compose logs redis`
- **Sistema**: `logs/health-check.log`
- **Backup**: `logs/backup.log`
- **Deploy**: `logs/deploy.log`

#### Comandos Úteis
```bash
# Logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f app

# Logs com timestamp
docker-compose -f docker-compose.prod.yml logs -t app

# Filtrar por nível de log
docker-compose -f docker-compose.prod.yml logs app | grep ERROR

# Exportar logs
docker-compose -f docker-compose.prod.yml logs app > app-logs-$(date +%Y%m%d).log
```

## Atualizações

### Deploy de Nova Versão
```bash
# 1. Backup antes da atualização
./scripts/backup.sh

# 2. Baixar nova versão
git pull origin main

# 3. Deploy com downtime mínimo
./scripts/deploy.sh

# 4. Verificar saúde
./scripts/health-check.sh

# 5. Rollback se necessário
# docker-compose -f docker-compose.prod.yml down
# git checkout versao-anterior
# ./scripts/deploy.sh
```

### Atualizações sem Downtime
```bash
# 1. Deploy em ambiente de staging
# 2. Testes automatizados
# 3. Deploy gradual com load balancer
# 4. Monitoramento contínuo
```

## Segurança

### Checklist de Segurança
- ✅ SSL/TLS configurado e funcional
- ✅ Senhas fortes para todos os serviços
- ✅ Firewall configurado (portas 80, 443, 22 apenas)
- ✅ Updates automáticos do sistema operacional
- ✅ Backup criptografado
- ✅ Monitoramento de tentativas de login
- ✅ Rate limiting no Nginx
- ✅ Headers de segurança configurados
- ✅ Logs de auditoria habilitados

### Comandos de Verificação
```bash
# Portas abertas
sudo netstat -tlnp

# Firewall status
sudo ufw status

# Certificados SSL
sudo certbot certificates

# Headers de segurança
curl -I https://agrotech.pt | grep -E "(Strict-Transport|X-Frame|X-Content)"
```

## Monitoramento Contínuo

### Métricas-Chave
- **Disponibilidade**: > 99.9%
- **Tempo de resposta**: < 2 segundos
- **CPU**: < 70%
- **Memória**: < 80%
- **Disco**: > 20% livre
- **Backup**: Diário, sem falhas

### Alertas Configurados
- Aplicação indisponível (crítico)
- Alta utilização de recursos (warning)
- Falha no backup (warning)
- Certificado SSL expirando (info)
- Taxa de erro elevada (warning)

### Dashboards
- **Sistema**: CPU, memória, disco, rede
- **Aplicação**: Requisições, erros, usuários
- **Base de dados**: Conexões, queries, performance
- **Negócio**: Usuários ativos, culturas cadastradas

## Suporte e Manutenção

### Contatos de Emergência
- **Admin Principal**: admin@agrotech.pt
- **Suporte Técnico**: suporte@agrotech.pt
- **Escalação**: emergencia@agrotech.pt

### Procedimentos de Emergência
1. **Aplicação Indisponível**:
   - Verificar health check
   - Analisar logs
   - Reiniciar serviços
   - Escalar se necessário

2. **Alta Carga**:
   - Monitorar recursos
   - Identificar gargalos
   - Implementar cache adicional
   - Considerar scaling horizontal

3. **Comprometimento de Segurança**:
   - Isolar sistema
   - Analisar logs de auditoria
   - Notificar usuários
   - Implementar correções
   - Relatório pós-incidente

### Manutenção Preventiva
- **Semanal**: Verificação de logs e métricas
- **Mensal**: Teste de backup e restore
- **Trimestral**: Atualização de dependências
- **Semestral**: Auditoria de segurança
- **Anual**: Revisão completa da arquitetura

Esta documentação deve ser mantida atualizada conforme evolução da plataforma e mudanças na infraestrutura.
