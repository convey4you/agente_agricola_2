# AgroTech 1.0 - Runbook de Troubleshooting
## Guia de Resolução de Problemas do Pipeline CI/CD

### 🚨 Procedimentos de Emergência

#### 1. Aplicação Down em Produção

**Sintomas**:
- Health checks falhando
- Usuários reportando erro 500/502
- Alertas críticos no Slack/PagerDuty

**Ações Imediatas** (< 5 minutos):
```bash
# 1. Verificar status dos pods
kubectl get pods -n agrotech-production -l app=agrotech

# 2. Verificar logs recentes
kubectl logs -n agrotech-production -l app=agrotech --tail=50

# 3. Se deployment recente, fazer rollback imediato
kubectl rollout undo deployment/agrotech-app -n agrotech-production

# 4. Verificar status do rollback
kubectl rollout status deployment/agrotech-app -n agrotech-production
```

**Investigação Detalhada**:
```bash
# Verificar eventos do cluster
kubectl get events -n agrotech-production --sort-by='.lastTimestamp'

# Verificar recursos (CPU/Memory)
kubectl top pods -n agrotech-production

# Verificar configuração do deployment
kubectl describe deployment agrotech-app -n agrotech-production
```

#### 2. Falha no Pipeline CI/CD

**Sintomas**:
- GitHub Actions falhando
- Deploy não completado
- Testes falhando inconsistentemente

**Diagnóstico**:
```bash
# Verificar logs do GitHub Actions
# Acessar: https://github.com/[org]/[repo]/actions

# Para falhas de teste, executar localmente:
python -m pytest tests/ -v --tb=short

# Para falhas de Docker build:
docker build -t agrotech:debug . --no-cache

# Para falhas de deploy:
kubectl get deployment -n agrotech-staging agrotech-app
```

### 🔧 Problemas Comuns e Soluções

#### 1. Database Connection Issues

**Sintomas**:
- Logs: "Connection to database failed"
- Health check: Database status failed
- Aplicação iniciando mas falhando nas queries

**Diagnóstico**:
```bash
# Verificar pod do PostgreSQL
kubectl get pods -n agrotech-production -l app=postgres

# Verificar logs do banco
kubectl logs -n agrotech-production -l app=postgres --tail=100

# Testar conexão do pod da aplicação
kubectl exec -it -n agrotech-production <app-pod> -- \
  python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://user:pass@postgres:5432/agrotech')
    print('✅ Database connection OK')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

**Soluções**:
```bash
# 1. Restart do serviço de banco
kubectl rollout restart deployment/postgres -n agrotech-production

# 2. Verificar secrets de conexão
kubectl get secret postgres-secret -n agrotech-production -o yaml

# 3. Verificar ConfigMap de configuração
kubectl get configmap app-config -n agrotech-production -o yaml
```

#### 2. Redis Cache Issues

**Sintomas**:
- Performance degradada
- Cache miss rate alto
- Logs: "Redis connection timeout"

**Diagnóstico**:
```bash
# Verificar pod do Redis
kubectl get pods -n agrotech-production -l app=redis

# Conectar ao Redis e verificar status
kubectl exec -it -n agrotech-production <redis-pod> -- redis-cli
> ping
> info memory
> info stats
```

**Soluções**:
```bash
# 1. Restart do Redis
kubectl rollout restart deployment/redis -n agrotech-production

# 2. Clear cache se necessário
kubectl exec -it -n agrotech-production <redis-pod> -- redis-cli flushall

# 3. Verificar configuração de memória
kubectl describe pod <redis-pod> -n agrotech-production
```

#### 3. Docker Registry Issues

**Sintomas**:
- Pipeline falha no push da imagem
- "Authentication failed" no GitHub Actions
- Pull image timeout no Kubernetes

**Diagnóstico**:
```bash
# Verificar se imagem existe no registry
docker pull ghcr.io/[org]/agrotech:latest

# Verificar autenticação
echo $GITHUB_TOKEN | docker login ghcr.io -u [username] --password-stdin
```

**Soluções**:
```bash
# 1. Regenerar GitHub Token
# Settings > Developer settings > Personal access tokens

# 2. Atualizar secret no repositório
# Settings > Secrets > Actions > GITHUB_TOKEN

# 3. Limpar cache de imagens locais
docker system prune -a
```

#### 4. SSL Certificate Issues

**Sintomas**:
- HTTPS não funcionando
- Browser showing "Certificate not valid"
- Traefik logs com erros de certificado

**Diagnóstico**:
```bash
# Verificar certificados no Traefik
kubectl logs -n agrotech-production -l app=traefik

# Verificar status dos certificados
kubectl get certificate -n agrotech-production

# Testar SSL externamente
openssl s_client -connect agrotech.com:443 -servername agrotech.com
```

**Soluções**:
```bash
# 1. Forçar renovação do certificado
kubectl delete certificate tls-cert -n agrotech-production

# 2. Verificar configuração do Traefik
kubectl get ingressroute -n agrotech-production -o yaml

# 3. Verificar DNS
nslookup agrotech.com
```

### ⚡ Performance Issues

#### 1. High CPU Usage

**Sintomas**:
- Resposta lenta da aplicação
- Kubernetes HPA scaling up
- CPU metrics no Grafana acima de 80%

**Diagnóstico**:
```bash
# Verificar uso de CPU dos pods
kubectl top pods -n agrotech-production

# Verificar métricas detalhadas
kubectl exec -it -n agrotech-production <app-pod> -- top

# Analisar logs por queries lentas
kubectl logs -n agrotech-production -l app=agrotech | grep "slow"
```

**Soluções**:
```bash
# 1. Scale horizontal imediato
kubectl scale deployment agrotech-app --replicas=5 -n agrotech-production

# 2. Verificar queries de banco otimizadas
kubectl exec -it -n agrotech-production <postgres-pod> -- \
  psql -U agrotech_prod -c "
  SELECT query, mean_time, calls 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC LIMIT 10;"

# 3. Analisar profiling da aplicação
# Implementar py-spy ou similar
```

#### 2. Memory Leaks

**Sintomas**:
- Pods sendo killed por OOM
- Memory usage crescente no Grafana
- Pods reiniciando frequentemente

**Diagnóstico**:
```bash
# Verificar memory usage
kubectl top pods -n agrotech-production

# Verificar events de OOM
kubectl get events -n agrotech-production | grep OOM

# Memory profiling dentro do pod
kubectl exec -it -n agrotech-production <app-pod> -- \
  python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

**Soluções**:
```bash
# 1. Aumentar memory limits temporariamente
kubectl patch deployment agrotech-app -n agrotech-production -p='
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "agrotech",
          "resources": {
            "limits": {
              "memory": "1Gi"
            }
          }
        }]
      }
    }
  }
}'

# 2. Restart dos pods
kubectl delete pods -n agrotech-production -l app=agrotech

# 3. Investigar código para memory leaks
# Implementar memory profiling com pympler
```

### 🔐 Security Issues

#### 1. Failed Security Scans

**Sintomas**:
- GitHub Actions security workflow falhando
- Vulnerabilidades detectadas
- Container scan bloqueando deploy

**Diagnóstico**:
```bash
# Executar scan local
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image agrotech:latest

# Verificar dependencies
safety check -r requirements.txt

# Scan de secrets
trufflehog filesystem . --only-verified
```

**Soluções**:
```bash
# 1. Atualizar dependências vulneráveis
pip-audit --fix

# 2. Atualizar imagem base
# Mudar FROM python:3.11-slim para versão mais recente

# 3. Remover secrets hardcoded
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret/file' HEAD
```

#### 2. Suspicious Login Activity

**Sintomas**:
- Alertas de segurança por login suspeito
- Múltiplas tentativas de login falhadas
- Acessos de IPs não autorizados

**Diagnóstico**:
```bash
# Verificar logs de autenticação
kubectl logs -n agrotech-production -l app=agrotech | grep "authentication"

# Verificar tentativas de login
kubectl exec -it -n agrotech-production <app-pod> -- \
  python -c "
from src.models.user import User
failed_logins = User.query.filter(
    User.last_login_attempt > datetime.now() - timedelta(hours=1),
    User.login_successful == False
).all()
print(f'Failed logins: {len(failed_logins)}')
"
```

**Soluções**:
```bash
# 1. Implementar rate limiting
# Adicionar nginx rate limiting na configuração

# 2. Bloqueio temporário de IPs suspeitos
kubectl exec -it -n agrotech-production <traefik-pod> -- \
  # Adicionar IP block no Traefik

# 3. Reset de senhas comprometidas
# Executar script de reset via banco de dados
```

### 📊 Monitoring and Alerting Issues

#### 1. Grafana Dashboard Not Loading

**Sintomas**:
- Grafana inacessível
- Dashboards sem dados
- Prometheus targets down

**Diagnóstico**:
```bash
# Verificar pods de monitoramento
kubectl get pods -n monitoring

# Verificar logs do Grafana
kubectl logs -n monitoring -l app=grafana

# Verificar Prometheus targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Acessar http://localhost:9090/targets
```

**Soluções**:
```bash
# 1. Restart do stack de monitoramento
kubectl rollout restart deployment/grafana -n monitoring
kubectl rollout restart deployment/prometheus -n monitoring

# 2. Verificar configuração do Prometheus
kubectl get configmap prometheus-config -n monitoring -o yaml

# 3. Recriar dashboards
# Import dashboards via Grafana UI ou API
```

#### 2. Alerts Not Firing

**Sintomas**:
- Problemas não notificados
- Alertmanager silent
- Slack não recebendo notificações

**Diagnóstico**:
```bash
# Verificar Alertmanager
kubectl logs -n monitoring -l app=alertmanager

# Verificar regras de alerta
kubectl get prometheusrule -n monitoring -o yaml

# Testar webhook do Slack
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' \
  $SLACK_WEBHOOK_URL
```

**Soluções**:
```bash
# 1. Verificar configuração do Alertmanager
kubectl edit configmap alertmanager-config -n monitoring

# 2. Testar regras de alerta
# Causar condição de alerta propositalmente

# 3. Verificar secrets de notificação
kubectl get secret alert-secrets -n monitoring -o yaml
```

### 🗄️ Database Issues

#### 1. Database Performance Degradation

**Sintomas**:
- Queries lentas
- Timeout em operações
- CPU do banco alto

**Diagnóstico**:
```bash
# Conectar ao banco e verificar queries ativas
kubectl exec -it -n agrotech-production <postgres-pod> -- \
  psql -U agrotech_prod -c "
  SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
  FROM pg_stat_activity 
  WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"

# Verificar locks
kubectl exec -it -n agrotech-production <postgres-pod> -- \
  psql -U agrotech_prod -c "
  SELECT blocked_locks.pid AS blocked_pid,
         blocking_locks.pid AS blocking_pid,
         blocked_activity.query AS blocked_statement
  FROM pg_catalog.pg_locks blocked_locks
  JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid;"
```

**Soluções**:
```bash
# 1. Kill queries longas se necessário
kubectl exec -it -n agrotech-production <postgres-pod> -- \
  psql -U agrotech_prod -c "SELECT pg_terminate_backend(<pid>);"

# 2. Reindex tabelas grandes
kubectl exec -it -n agrotech-production <postgres-pod> -- \
  psql -U agrotech_prod -c "REINDEX DATABASE agrotech_prod;"

# 3. Atualizar estatísticas
kubectl exec -it -n agrotech-production <postgres-pod> -- \
  psql -U agrotech_prod -c "ANALYZE;"
```

### 📞 Escalation Procedures

#### Level 1 - DevOps Engineer (0-15 min)
- Verificar logs e métricas
- Executar troubleshooting básico
- Implementar fixes rápidos (restart, rollback)

#### Level 2 - Senior DevOps/Platform Team (15-30 min)
- Análise profunda de logs
- Investigação de infraestrutura
- Coordenação com outras equipes

#### Level 3 - Architecture Team (30+ min)
- Problemas de design/arquitetura
- Mudanças estruturais necessárias
- Planning de melhorias

### 📋 Checklist Pós-Incidente

**Imediato**:
- [ ] Problema resolvido?
- [ ] Usuários notificados?
- [ ] Monitoramento normal?
- [ ] Logs limpos?

**Follow-up (24h)**:
- [ ] Post-mortem agendado
- [ ] Root cause identificada
- [ ] Preventive measures definidas
- [ ] Documentation atualizada

**Long-term**:
- [ ] Monitoring melhorado
- [ ] Alertas ajustados
- [ ] Processes atualizados
- [ ] Training conduzido

### 🔧 Ferramentas Úteis

#### Scripts de Diagnóstico
```bash
# Quick health check script
#!/bin/bash
echo "=== AgroTech Health Check ==="
kubectl get pods -n agrotech-production
kubectl get svc -n agrotech-production
kubectl top nodes
echo "=== Recent Events ==="
kubectl get events -n agrotech-production --sort-by='.lastTimestamp' | tail -10
```

#### Log Analysis
```bash
# Aggregate error logs
kubectl logs -n agrotech-production -l app=agrotech --since=1h | \
  grep -i error | sort | uniq -c | sort -nr

# Monitor real-time logs
kubectl logs -n agrotech-production -l app=agrotech -f
```

### 📞 Contatos de Emergência

- **DevOps On-Call**: +55 11 9999-0001
- **Security Team**: +55 11 9999-0002  
- **Database Team**: +55 11 9999-0003
- **Product Owner**: +55 11 9999-0004

**Slack Channels**:
- `#agrotech-incidents` - Incidentes críticos
- `#agrotech-deploys` - Deploy notifications
- `#agrotech-alerts` - Monitoring alerts

---

**Última Atualização**: $(date)
**Versão**: 1.0.0
**Autor**: DevOps Team
