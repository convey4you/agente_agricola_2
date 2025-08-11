# Sistema de Backup AgroTech 1.0 - Documentação Completa

## Visão Geral

O Sistema de Backup AgroTech 1.0 é uma solução empresarial robusta desenvolvida para proteger todos os componentes críticos do projeto durante e após suas refatorações significativas. O sistema oferece backup automatizado, verificação de integridade, restauração granular e monitoramento contínuo.

## Estrutura do Sistema

```
backups/
├── scripts/
│   ├── backup_manager.py         # Orquestrador principal
│   ├── database_backup.py        # Backup especializado de banco
│   ├── code_backup.py           # Backup de código com Git
│   ├── restore_manager.py       # Sistema de restauração
│   ├── verify_integrity.py      # Verificação de integridade
│   ├── setup_cron.py           # Configuração de automação
│   ├── send_notification.py    # Notificações (auto-gerado)
│   └── test_restore_routine.py  # Testes automáticos (auto-gerado)
├── logs/                        # Logs de execução
├── reports/                     # Relatórios de integridade
├── storage/                     # Armazenamento de backups
│   ├── database/               # Backups de banco de dados
│   ├── code/                   # Backups de código fonte
│   ├── config/                 # Backups de configurações
│   └── assets/                 # Backups de assets
└── temp/                       # Arquivos temporários
```

## Componentes Principais

### 1. Gerenciador Principal (backup_manager.py)

**Funcionalidades:**
- Orquestração de todos os tipos de backup
- Agendamento e automação
- Sistema de notificações
- Limpeza automática de backups antigos
- Compressão e criptografia

**Tipos de Backup:**
- **Completo**: Backup integral de todos os componentes
- **Incremental**: Apenas mudanças desde o último backup
- **Diferencial**: Mudanças desde o último backup completo
- **Pré-deploy**: Backup de segurança antes de atualizações

**Uso:**
```bash
# Backup completo
python backups/scripts/backup_manager.py --type full

# Backup incremental
python backups/scripts/backup_manager.py --type incremental

# Limpeza automática
python backups/scripts/backup_manager.py --cleanup

# Backup com notificação
python backups/scripts/backup_manager.py --type full --notify
```

### 2. Backup de Banco de Dados (database_backup.py)

**Características:**
- Suporte a SQLite e PostgreSQL/SQLAlchemy
- Backup de schema e dados
- Anonimização de dados sensíveis
- Backup incremental inteligente
- Verificação de consistência

**Recursos Especiais:**
- Backup de estrutura separado dos dados
- Anonimização de emails, CPFs, senhas
- Backup incremental baseado em timestamps
- Compressão otimizada para dados

**Configuração de Anonimização:**
```python
anonymization_rules = {
    'users': {
        'email': 'fake_email',
        'password': 'hash_password',
        'cpf': 'fake_cpf'
    }
}
```

### 3. Backup de Código (code_backup.py)

**Funcionalidades:**
- Integração completa com Git
- Análise de métricas de código
- Backup de histórico de commits
- Exclusão inteligente de arquivos
- Análise de complexidade

**Métricas Coletadas:**
- Linhas de código por linguagem
- Complexidade ciclomática
- Cobertura de testes
- Dependências do projeto
- Histórico de mudanças

**Filtros Automáticos:**
- Arquivos de cache (`__pycache__`, `.pyc`)
- Dependências (`node_modules`, `venv`)
- Arquivos de sistema (`.DS_Store`, `Thumbs.db`)
- Logs e temporários

### 4. Sistema de Restauração (restore_manager.py)

**Capacidades:**
- Restauração granular por componente
- Rollback automático em caso de falha
- Teste de restauração sem impacto
- Restauração seletiva de arquivos
- Múltiplos pontos de restauração

**Tipos de Restauração:**
- **Completa**: Restaura todos os componentes
- **Seletiva**: Restaura componentes específicos
- **Pontual**: Restaura para timestamp específico
- **Teste**: Simula restauração sem alterações

**Exemplo de Uso:**
```bash
# Listar backups disponíveis
python backups/scripts/restore_manager.py --list

# Restaurar backup completo mais recente
python backups/scripts/restore_manager.py --restore latest --type full

# Restaurar apenas banco de dados
python backups/scripts/restore_manager.py --restore latest --component database

# Teste de restauração
python backups/scripts/restore_manager.py --test-restore latest
```

### 5. Verificação de Integridade (verify_integrity.py)

**Validações:**
- Checksums SHA256 de todos os arquivos
- Verificação de estrutura de backups
- Testes de descompressão
- Validação de conteúdo
- Simulação de restauração

**Relatórios Gerados:**
- Status de integridade por backup
- Tempo de verificação
- Problemas identificados
- Recomendações de ação
- Histórico de verificações

**Classificações de Status:**
- **Excelente**: Todas as verificações passaram
- **Bom**: Verificações principais OK, alertas menores
- **Regular**: Alguns problemas identificados
- **Crítico**: Problemas sérios detectados
- **Falha**: Backup corrompido ou inacessível

## Configuração e Instalação

### 1. Instalação do Sistema

```bash
# Clonar/verificar estrutura do projeto
cd agente_agricola

# Verificar se os scripts estão presentes
ls -la backups/scripts/

# Configurar ambiente Python (se necessário)
python -m pip install -r requirements.txt
```

### 2. Configuração de Variáveis de Ambiente

Criar arquivo `.env` ou configurar no sistema:

```bash
# Banco de dados
DATABASE_URL="sqlite:///path/to/database.db"
# ou
DATABASE_URL="postgresql://user:pass@localhost/dbname"

# Notificações por email
BACKUP_EMAIL_USER="seu.email@gmail.com"
BACKUP_EMAIL_PASSWORD="sua_senha_app"
BACKUP_NOTIFICATION_EMAILS="admin@agrotech.com,backup@agrotech.com"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"

# Configurações de backup
BACKUP_RETENTION_DAYS="30"
BACKUP_COMPRESSION_LEVEL="6"
BACKUP_ENCRYPTION_KEY="sua_chave_secreta"
```

### 3. Configuração de Cron Jobs

```bash
# Instalar cron jobs automaticamente
python backups/scripts/setup_cron.py --install

# Verificar instalação
python backups/scripts/setup_cron.py --list

# Testar ambiente
python backups/scripts/setup_cron.py --test
```

**Agendamento Padrão:**
- **02:00 diário**: Backup incremental
- **01:00 domingo**: Backup completo semanal
- **03:30 diário**: Limpeza de backups antigos
- **04:00 segunda**: Verificação de integridade
- **00:00 dia 1**: Backup completo mensal
- **05:00 dia 1**: Teste de restauração mensal

## Procedimentos Operacionais

### Backup Manual

```bash
# Backup completo antes de deploy
python backups/scripts/backup_manager.py --type full --tag "pre-deploy-v2.1"

# Backup incremental manual
python backups/scripts/backup_manager.py --type incremental --notify

# Backup específico do banco
python backups/scripts/database_backup.py --full --anonymize
```

### Verificação de Integridade

```bash
# Verificação completa
python backups/scripts/verify_integrity.py --comprehensive --generate-report

# Verificação rápida
python backups/scripts/verify_integrity.py --health-check

# Verificar backup específico
python backups/scripts/verify_integrity.py --verify-file /path/to/backup.tar.gz
```

### Restauração

```bash
# Listar backups disponíveis
python backups/scripts/restore_manager.py --list

# Restauração interativa
python backups/scripts/restore_manager.py --interactive

# Restauração específica
python backups/scripts/restore_manager.py --restore "2024-01-15_14-30-00" --component database

# Rollback para estado anterior
python backups/scripts/restore_manager.py --rollback --backup-before-restore
```

## Monitoramento e Alertas

### Logs do Sistema

**Localização:** `backups/logs/`
- `backup_daily.log`: Backups incrementais diários
- `backup_weekly.log`: Backups completos semanais
- `cleanup.log`: Limpeza automática
- `integrity_check.log`: Verificações de integridade
- `restore.log`: Operações de restauração

### Notificações por Email

**Triggers de Notificação:**
- Falha em qualquer backup
- Problemas de integridade detectados
- Espaço em disco baixo
- Backups antigos não removidos
- Testes de restauração falharam

**Formato das Notificações:**
```
Assunto: AgroTech Backup - [JOB] - [STATUS]

Conteúdo:
- Nome do job executado
- Status da execução
- Timestamp
- Últimas linhas do log
- Ações recomendadas
```

### Métricas e Relatórios

**Relatórios Automáticos:**
- Relatório semanal de integridade
- Relatório mensal de uso de espaço
- Relatório de testes de restauração
- Análise de performance de backups

**Localização:** `backups/reports/`

## Disaster Recovery

### Cenários de Recuperação

#### 1. Falha Completa do Sistema
```bash
# 1. Configurar novo ambiente
# 2. Restaurar backup completo mais recente
python backups/scripts/restore_manager.py --restore latest --type full --force

# 3. Verificar integridade
python backups/scripts/verify_integrity.py --health-check

# 4. Testar funcionalidade
python src/main.py --test-mode
```

#### 2. Corrupção de Banco de Dados
```bash
# 1. Parar aplicação
# 2. Fazer backup do estado atual (para investigação)
python backups/scripts/database_backup.py --emergency-backup

# 3. Restaurar backup de banco mais recente
python backups/scripts/restore_manager.py --restore latest --component database

# 4. Verificar consistência
python backups/scripts/database_backup.py --verify-integrity
```

#### 3. Perda de Código Fonte
```bash
# 1. Restaurar código mais recente
python backups/scripts/restore_manager.py --restore latest --component code

# 2. Verificar repositório Git
cd src && git status

# 3. Restaurar dependências
pip install -r requirements.txt
```

### Plano de Contingência

**RTO (Recovery Time Objective):** 4 horas
**RPO (Recovery Point Objective):** 24 horas (backup diário)

**Procedimento de Emergência:**
1. **Identificação** (15 min): Diagnosticar tipo de falha
2. **Isolamento** (30 min): Isolar componentes afetados
3. **Recuperação** (2-3 horas): Restaurar backups necessários
4. **Verificação** (30 min): Testar funcionalidade
5. **Documentação** (15 min): Registrar incidente

## Manutenção e Otimização

### Manutenção Mensal

```bash
# 1. Verificação completa de integridade
python backups/scripts/verify_integrity.py --comprehensive --generate-report

# 2. Limpeza manual de arquivos antigos
python backups/scripts/backup_manager.py --cleanup --force

# 3. Teste completo de restauração
python backups/scripts/test_restore_routine.py

# 4. Análise de performance
python backups/scripts/backup_manager.py --performance-report

# 5. Atualização de configurações se necessário
python backups/scripts/setup_cron.py --test
```

### Otimização de Espaço

**Configurações Recomendadas:**
- Retenção: 30 dias para incrementais, 90 dias para completos
- Compressão: Nível 6 (equilíbrio entre velocidade e tamanho)
- Limpeza automática: Diária às 03:30
- Verificação de integridade: Semanal

**Comandos de Otimização:**
```bash
# Análise de uso de espaço
du -sh backups/storage/*

# Compactação adicional de backups antigos
find backups/storage -name "*.tar.gz" -mtime +30 -exec gzip {} \;

# Limpeza de logs antigos
find backups/logs -name "*.log" -mtime +90 -delete
```

## Troubleshooting

### Problemas Comuns

#### 1. Backup Falha com "Permission Denied"
```bash
# Verificar permissões
ls -la backups/
chmod -R 755 backups/scripts/
chmod -R 766 backups/storage/
```

#### 2. Cron Jobs Não Executam
```bash
# Verificar crontab
crontab -l | grep AgroTech

# Testar ambiente
python backups/scripts/setup_cron.py --test

# Verificar logs do cron
tail -f /var/log/cron
```

#### 3. Email de Notificação Não Funciona
```bash
# Testar configuração de email
python -c "
import os
print('SMTP:', os.getenv('SMTP_SERVER'))
print('User:', os.getenv('BACKUP_EMAIL_USER'))
print('Recipients:', os.getenv('BACKUP_NOTIFICATION_EMAILS'))
"

# Teste manual de envio
python backups/scripts/send_notification.py --job test --status success
```

#### 4. Backup Muito Lento
```bash
# Verificar espaço em disco
df -h

# Analisar tamanho dos componentes
du -sh src/ static/ logs/

# Otimizar compressão
# Editar backup_manager.py: compression_level = 3
```

#### 5. Restauração Falha
```bash
# Verificar integridade do backup
python backups/scripts/verify_integrity.py --verify-file backup_file.tar.gz

# Testar restauração sem aplicar
python backups/scripts/restore_manager.py --test-restore backup_file.tar.gz

# Verificar espaço disponível
df -h
```

## Segurança

### Medidas de Segurança Implementadas

1. **Criptografia**: Backups podem ser criptografados com AES-256
2. **Anonimização**: Dados sensíveis são anonimizados automaticamente
3. **Checksums**: Verificação SHA256 de todos os arquivos
4. **Permissões**: Acesso restrito aos diretórios de backup
5. **Logs Seguros**: Senhas e dados sensíveis não aparecem em logs

### Configuração de Segurança

```bash
# Configurar criptografia
export BACKUP_ENCRYPTION_KEY="sua_chave_muito_secreta_256_bits"

# Configurar permissões restritivas
chmod 700 backups/storage/
chmod 600 backups/storage/*

# Configurar usuário específico para backups
sudo useradd backup-user
sudo chown -R backup-user:backup-user backups/
```

## Performance

### Benchmarks Típicos

**Ambiente de Teste:**
- CPU: 4 cores, 2.5GHz
- RAM: 8GB
- Disco: SSD SATA
- Projeto: ~500MB

**Tempos Médios:**
- Backup Incremental: 2-5 minutos
- Backup Completo: 10-15 minutos
- Verificação de Integridade: 5-8 minutos
- Restauração Completa: 8-12 minutos

**Otimizações Aplicadas:**
- Compressão paralela quando possível
- Exclusão inteligente de arquivos desnecessários
- Backup incremental baseado em checksums
- Cache de metadados para operações repetidas

## Conclusão

O Sistema de Backup AgroTech 1.0 oferece proteção empresarial completa para o projeto, garantindo:

✅ **Proteção Completa**: Todos os componentes críticos protegidos
✅ **Automação Total**: Backups automáticos sem intervenção manual
✅ **Recuperação Rápida**: RTO de 4 horas para cenários críticos
✅ **Integridade Garantida**: Verificação contínua de todos os backups
✅ **Monitoramento Ativo**: Alertas proativos para problemas
✅ **Escalabilidade**: Suporta crescimento do projeto
✅ **Segurança**: Criptografia e anonimização de dados sensíveis

O sistema foi projetado para operar de forma autônoma, requerendo manutenção mínima enquanto oferece máxima proteção aos dados e código do projeto AgroTech 1.0.

---

**Versão da Documentação:** 1.0  
**Data de Criação:** Janeiro 2024  
**Última Atualização:** Janeiro 2024  
**Responsável:** Sistema de Backup AgroTech 1.0
