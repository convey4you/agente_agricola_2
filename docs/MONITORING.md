# Documentação de Monitoramento - AgroTech Portugal

## Visão Geral

O sistema de monitoramento do AgroTech Portugal é baseado em Prometheus e Grafana, proporcionando visibilidade completa sobre a saúde, performance e utilização da plataforma.

## Componentes do Sistema

### 1. Prometheus
- **Porta**: 9090
- **Função**: Coleta e armazenamento de métricas
- **Configuração**: `monitoring/prometheus.yml`
- **Retenção**: 15 dias de dados

### 2. Grafana
- **Porta**: 3000
- **Função**: Visualização e dashboards
- **Credenciais padrão**: admin/admin (alterar no primeiro acesso)
- **Dashboards**: `monitoring/grafana/dashboards/`

### 3. Alertas
- **Configuração**: `monitoring/alerts.yml`
- **Canais**: Email, Slack, Webhook
- **Níveis**: Critical, Warning, Info

## Métricas Coletadas

### Métricas de Sistema
```
# CPU
node_cpu_seconds_total
process_cpu_seconds_total

# Memória
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes
container_memory_usage_bytes

# Disco
node_filesystem_size_bytes
node_filesystem_free_bytes

# Rede
node_network_receive_bytes_total
node_network_transmit_bytes_total
```

### Métricas de Aplicação
```
# Flask
flask_http_request_total
flask_http_request_duration_seconds
flask_http_request_exceptions_total

# Usuários
agrotech_active_users
agrotech_login_attempts_total
agrotech_failed_login_attempts_total

# Features
agrotech_dashboard_views_total
agrotech_culture_updates_total
agrotech_weather_requests_total
```

### Métricas de Base de Dados
```
# PostgreSQL
pg_up
pg_stat_activity_count
pg_stat_database_tup_returned
pg_stat_database_tup_fetched
pg_database_size_bytes

# Queries
pg_stat_statements_calls
pg_stat_statements_mean_time
```

### Métricas de Cache
```
# Redis
redis_up
redis_memory_used_bytes
redis_memory_max_bytes
redis_connected_clients
redis_keyspace_hits_total
redis_keyspace_misses_total
```

## Dashboards Disponíveis

### 1. AgroTech Overview
- **Arquivo**: `agrotech-overview.json`
- **Conteúdo**:
  - Status geral dos serviços
  - Métricas de performance
  - Gráficos de utilização
  - Alertas ativos

### 2. Sistema (Node Exporter)
- CPU, Memória, Disco
- Rede e I/O
- Load average
- Processos

### 3. Base de Dados
- Conexões ativas
- Performance de queries
- Tamanho das tabelas
- Cache hit ratio

### 4. Aplicação
- Requisições HTTP
- Tempos de resposta
- Erros e exceções
- Usuários ativos

## Alertas Configurados

### Críticos
- ✗ Aplicação indisponível (2 min)
- ✗ PostgreSQL indisponível (1 min)
- ✗ Nginx proxy indisponível (1 min)

### Warnings
- ⚠️ CPU > 80% (5 min)
- ⚠️ Memória > 85% (3 min)
- ⚠️ Disco < 15% livre (2 min)
- ⚠️ Taxa de erro > 5% (3 min)
- ⚠️ Muitas conexões BD (3 min)
- ⚠️ Latência alta > 2s (3 min)

### Informativos
- ℹ️ Poucos usuários ativos (10 min)
- ℹ️ Backup não executado (24h)
- ℹ️ Certificado SSL expirando (30 dias)

## Scripts de Monitoramento

### 1. Health Check
```bash
# Execução manual
./scripts/health-check.sh

# Via cron (a cada 5 minutos)
*/5 * * * * /path/to/scripts/health-check.sh >> /var/log/agrotech-health.log 2>&1
```

**Verificações realizadas**:
- Status dos containers
- Conectividade HTTP
- Base de dados PostgreSQL
- Cache Redis
- Uso de recursos
- Logs de erro
- Geração de métricas customizadas

### 2. Coleta de Métricas
```bash
# Arquivo gerado
/tmp/agrotech-metrics.prom

# Métricas incluídas
agrotech_service_up{service="app|db|redis|nginx"}
agrotech_active_users
agrotech_last_backup_timestamp
agrotech_api_response_time
```

## Configuração de Alertas

### Email (SMTP)
```yaml
# Em docker-compose.prod.yml
environment:
  - SMTP_SERVER=smtp.gmail.com
  - SMTP_PORT=587
  - SMTP_USER=alerts@agrotech.pt
  - SMTP_PASSWORD=senha_aplicacao
  - ALERT_EMAIL=admin@agrotech.pt
```

### Slack
```yaml
# Webhook URL
environment:
  - SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Webhook Personalizado
```yaml
environment:
  - ALERT_WEBHOOK_URL=https://api.agrotech.pt/alerts
```

## Acesso aos Dashboards

### URLs de Acesso
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Alertmanager**: http://localhost:9093

### Configuração SSL (Produção)
```nginx
# nginx/nginx.conf
location /monitoring/ {
    auth_basic "Monitoring";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    location /monitoring/grafana/ {
        proxy_pass http://grafana:3000/;
    }
    
    location /monitoring/prometheus/ {
        proxy_pass http://prometheus:9090/;
    }
}
```

## Troubleshooting

### Prometheus não coleta métricas
```bash
# Verificar configuração
docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Verificar targets
curl http://localhost:9090/api/v1/targets

# Logs
docker-compose logs prometheus
```

### Grafana não mostra dados
```bash
# Verificar datasource
curl http://admin:admin@localhost:3000/api/datasources

# Testar conectividade
docker-compose exec grafana curl http://prometheus:9090/api/v1/query?query=up

# Logs
docker-compose logs grafana
```

### Alertas não funcionam
```bash
# Verificar regras
docker-compose exec prometheus promtool check rules /etc/prometheus/alerts.yml

# Status dos alertas
curl http://localhost:9090/api/v1/alerts

# Logs do alertmanager
docker-compose logs alertmanager
```

## Backup de Configurações

### Prometheus
```bash
# Backup configuração
cp monitoring/prometheus.yml backups/prometheus-$(date +%Y%m%d).yml

# Backup dados (se necessário)
docker-compose exec prometheus tar -czf /tmp/prometheus-data.tar.gz /prometheus
```

### Grafana
```bash
# Export dashboards
curl -u admin:admin http://localhost:3000/api/search | jq '.[] | .uid' | xargs -I {} curl -u admin:admin http://localhost:3000/api/dashboards/uid/{} > grafana-dashboards-backup.json

# Backup configurações
docker-compose exec grafana tar -czf /tmp/grafana-config.tar.gz /etc/grafana
```

## Otimização de Performance

### Prometheus
- Ajustar intervalo de scraping conforme necessário
- Configurar retention baseado no uso de disco
- Usar recording rules para queries complexas

### Grafana
- Limitar tempo de queries nos dashboards
- Usar cache para consultas frequentes
- Otimizar painéis com muitos dados

### Alertas
- Agrupar alertas similares
- Configurar silencing para manutenções
- Usar routing inteligente por severidade

## Segurança

### Autenticação
- Alterar senhas padrão
- Usar LDAP/OAuth quando disponível
- Configurar roles e permissões

### Rede
- Expor apenas portas necessárias
- Usar SSL/TLS em produção
- Configurar firewall adequadamente

### Dados
- Evitar métricas com dados sensíveis
- Configurar retenção apropriada
- Backup regular das configurações

## Métricas Customizadas

### Adicionar Nova Métrica
1. **No código Python**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Contador
user_logins = Counter('agrotech_user_logins_total', 'Total user logins')

# Histograma
request_duration = Histogram('agrotech_request_duration_seconds', 'Request duration')

# Gauge
active_users = Gauge('agrotech_active_users', 'Currently active users')
```

2. **Endpoint de métricas**:
```python
from prometheus_client import generate_latest

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain'}
```

3. **Configurar coleta**:
```yaml
# prometheus.yml
- job_name: 'agrotech-custom'
  static_configs:
    - targets: ['app:5000']
  metrics_path: /metrics
```

## Integração com Logs

### Configuração Loki (Opcional)
```yaml
# docker-compose.prod.yml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  volumes:
    - ./monitoring/loki:/etc/loki

promtail:
  image: grafana/promtail:latest
  volumes:
    - ./logs:/var/log
    - ./monitoring/promtail:/etc/promtail
```

Essa documentação fornece um guia completo para operar e manter o sistema de monitoramento do AgroTech Portugal.
