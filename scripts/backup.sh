#!/bin/bash
# Script de backup completo para AgroTech Portugal

set -e

# Configurações
DB_HOST="db"
DB_NAME="agrotech_prod"
DB_USER="agrotech"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Backup do banco de dados
backup_database() {
    log "Iniciando backup do banco de dados..."
    
    BACKUP_FILE="$BACKUP_DIR/agrotech_db_$DATE.sql"
    
    pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        log "Backup do banco de dados concluído: $BACKUP_FILE"
        
        # Comprimir backup
        gzip $BACKUP_FILE
        log "Backup comprimido: $BACKUP_FILE.gz"
        
        # Calcular checksum
        md5sum "$BACKUP_FILE.gz" > "$BACKUP_FILE.gz.md5"
        log "Checksum calculado: $BACKUP_FILE.gz.md5"
    else
        log "ERRO: Falha no backup do banco de dados"
        exit 1
    fi
}

# Backup de arquivos de upload
backup_uploads() {
    log "Iniciando backup de arquivos de upload..."
    
    UPLOADS_BACKUP="$BACKUP_DIR/agrotech_uploads_$DATE.tar.gz"
    
    if [ -d "/app/uploads" ]; then
        tar -czf $UPLOADS_BACKUP -C /app uploads/
        log "Backup de uploads concluído: $UPLOADS_BACKUP"
        
        # Calcular checksum
        md5sum $UPLOADS_BACKUP > "$UPLOADS_BACKUP.md5"
    else
        log "Diretório de uploads não encontrado, pulando..."
    fi
}

# Backup das configurações
backup_configs() {
    log "Iniciando backup das configurações..."
    
    CONFIG_BACKUP="$BACKUP_DIR/agrotech_configs_$DATE.tar.gz"
    
    tar -czf $CONFIG_BACKUP \
        /app/.env \
        /app/config.py \
        /nginx/nginx.conf \
        /monitoring/prometheus.yml \
        2>/dev/null || true
    
    if [ -f "$CONFIG_BACKUP" ]; then
        log "Backup de configurações concluído: $CONFIG_BACKUP"
        md5sum $CONFIG_BACKUP > "$CONFIG_BACKUP.md5"
    fi
}

# Limpeza de backups antigos
cleanup_old_backups() {
    log "Limpando backups antigos (mais de $RETENTION_DAYS dias)..."
    
    find $BACKUP_DIR -name "agrotech_*" -type f -mtime +$RETENTION_DAYS -delete
    
    log "Limpeza concluída"
}

# Verificar integridade do backup
verify_backup() {
    local backup_file="$1"
    
    log "Verificando integridade do backup: $backup_file"
    
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        log "Backup verificado com sucesso"
        return 0
    else
        log "ERRO: Backup inválido ou vazio"
        return 1
    fi
}

# Relatório de espaço
generate_report() {
    log "Gerando relatório de backup..."
    
    TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
    BACKUP_COUNT=$(ls -1 $BACKUP_DIR/*.gz 2>/dev/null | wc -l)
    
    log "Relatório de Backup:"
    log "  - Total de backups: $BACKUP_COUNT"
    log "  - Espaço utilizado: $TOTAL_SIZE"
    log "  - Localização: $BACKUP_DIR"
    log "  - Retenção: $RETENTION_DAYS dias"
}

# Enviar notificação de status
send_notification() {
    local status="$1"
    local message="$2"
    
    # Integração com webhook (Slack, Discord, etc.)
    if [ ! -z "$WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"AgroTech Backup [$status]: $message\"}" \
             $WEBHOOK_URL 2>/dev/null || true
    fi
    
    log "NOTIFICAÇÃO [$status]: $message"
}

# Função principal
main() {
    log "==================== INÍCIO DO BACKUP ===================="
    
    # Verificar dependências
    for cmd in pg_dump tar gzip md5sum; do
        if ! command -v $cmd &> /dev/null; then
            log "ERRO: Comando $cmd não encontrado"
            send_notification "ERROR" "Comando $cmd não encontrado no sistema"
            exit 1
        fi
    done
    
    # Executar backups
    backup_database
    backup_uploads
    backup_configs
    
    # Limpeza
    cleanup_old_backups
    
    # Relatório
    generate_report
    
    # Verificar se pelo menos o backup do banco existe
    DB_BACKUP="$BACKUP_DIR/agrotech_db_$DATE.sql.gz"
    if verify_backup "$DB_BACKUP"; then
        send_notification "SUCCESS" "Backup concluído com sucesso em $(date)"
        log "==================== BACKUP CONCLUÍDO ===================="
    else
        send_notification "ERROR" "Falha na verificação do backup"
        exit 1
    fi
}

# Executar função principal
main "$@"
