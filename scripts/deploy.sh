#!/bin/bash
# Script de deploy automatizado para AgroTech Portugal

set -e

# Configurações
PROJECT_NAME="agrotech"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
BACKUP_BEFORE_DEPLOY=true
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_ON_FAILURE=true

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de logging
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Verificar dependências
check_dependencies() {
    log "Verificando dependências..."
    
    for cmd in docker docker-compose git curl; do
        if ! command -v $cmd &> /dev/null; then
            log_error "Comando $cmd não encontrado"
            exit 1
        fi
    done
    
    log_success "Todas as dependências estão instaladas"
}

# Verificar arquivos necessários
check_files() {
    log "Verificando arquivos necessários..."
    
    required_files=(
        "$DOCKER_COMPOSE_FILE"
        "$ENV_FILE"
        "Dockerfile.prod"
        "nginx/nginx.conf"
        "scripts/backup.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Arquivo necessário não encontrado: $file"
            exit 1
        fi
    done
    
    log_success "Todos os arquivos necessários estão presentes"
}

# Fazer backup antes do deploy
create_backup() {
    if [ "$BACKUP_BEFORE_DEPLOY" = true ]; then
        log "Criando backup antes do deploy..."
        
        if [ -f "scripts/backup.sh" ]; then
            chmod +x scripts/backup.sh
            ./scripts/backup.sh
            log_success "Backup criado com sucesso"
        else
            log_warning "Script de backup não encontrado, pulando..."
        fi
    fi
}

# Parar serviços existentes
stop_services() {
    log "Parando serviços existentes..."
    
    docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans || true
    
    log_success "Serviços parados"
}

# Construir imagens
build_images() {
    log "Construindo novas imagens..."
    
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    if [ $? -eq 0 ]; then
        log_success "Imagens construídas com sucesso"
    else
        log_error "Falha na construção das imagens"
        exit 1
    fi
}

# Iniciar serviços
start_services() {
    log "Iniciando serviços..."
    
    # Carregar variáveis de ambiente
    export $(cat $ENV_FILE | grep -v '^#' | xargs)
    
    # Iniciar serviços em ordem
    docker-compose -f $DOCKER_COMPOSE_FILE up -d db redis
    
    log "Aguardando inicialização do banco de dados..."
    sleep 30
    
    docker-compose -f $DOCKER_COMPOSE_FILE up -d app
    
    log "Aguardando inicialização da aplicação..."
    sleep 20
    
    docker-compose -f $DOCKER_COMPOSE_FILE up -d nginx
    
    log "Aguardando inicialização do proxy..."
    sleep 10
    
    # Iniciar monitoramento
    docker-compose -f $DOCKER_COMPOSE_FILE up -d prometheus grafana node_exporter
    
    log_success "Todos os serviços iniciados"
}

# Verificar saúde dos serviços
health_check() {
    log "Verificando saúde dos serviços..."
    
    local timeout=$HEALTH_CHECK_TIMEOUT
    local counter=0
    local interval=10
    
    while [ $counter -lt $timeout ]; do
        # Verificar se a aplicação está respondendo
        if curl -f http://localhost/health &>/dev/null; then
            log_success "Aplicação está saudável"
            return 0
        fi
        
        log "Aguardando aplicação ficar saudável... ($counter/$timeout segundos)"
        sleep $interval
        counter=$((counter + interval))
    done
    
    log_error "Aplicação não ficou saudável dentro do tempo limite"
    return 1
}

# Executar testes de fumaça
smoke_tests() {
    log "Executando testes de fumaça..."
    
    # Teste 1: Endpoint de saúde
    if ! curl -f http://localhost/health &>/dev/null; then
        log_error "Teste de saúde falhou"
        return 1
    fi
    
    # Teste 2: Página inicial
    if ! curl -f http://localhost/ &>/dev/null; then
        log_error "Teste da página inicial falhou"
        return 1
    fi
    
    # Teste 3: API status
    if ! curl -f http://localhost/api/status &>/dev/null; then
        log_error "Teste da API falhou"
        return 1
    fi
    
    # Teste 4: Arquivos estáticos
    if ! curl -f http://localhost/static/css/design-system.css &>/dev/null; then
        log_error "Teste de arquivos estáticos falhou"
        return 1
    fi
    
    log_success "Todos os testes de fumaça passaram"
    return 0
}

# Verificar logs em busca de erros
check_logs() {
    log "Verificando logs em busca de erros..."
    
    # Verificar logs da aplicação
    app_errors=$(docker-compose -f $DOCKER_COMPOSE_FILE logs app | grep -i error | wc -l)
    
    if [ $app_errors -gt 0 ]; then
        log_warning "Encontrados $app_errors erros nos logs da aplicação"
        docker-compose -f $DOCKER_COMPOSE_FILE logs --tail=20 app
    else
        log_success "Nenhum erro encontrado nos logs da aplicação"
    fi
}

# Fazer rollback em caso de falha
rollback() {
    if [ "$ROLLBACK_ON_FAILURE" = true ]; then
        log_warning "Iniciando rollback..."
        
        # Parar serviços atuais
        docker-compose -f $DOCKER_COMPOSE_FILE down
        
        # Restaurar backup mais recente
        latest_backup=$(ls -t backups/agrotech_db_*.sql.gz 2>/dev/null | head -1)
        
        if [ -n "$latest_backup" ]; then
            log "Restaurando backup: $latest_backup"
            # Aqui você implementaria a lógica de restauração
            # Por enquanto apenas logamos
            log_warning "Rollback simulado (implementar lógica de restauração)"
        else
            log_error "Nenhum backup encontrado para rollback"
        fi
        
        log_warning "Rollback concluído"
    fi
}

# Enviar notificação de deploy
send_notification() {
    local status="$1"
    local message="$2"
    
    if [ ! -z "$WEBHOOK_URL" ]; then
        local color="good"
        if [ "$status" = "ERROR" ]; then
            color="danger"
        elif [ "$status" = "WARNING" ]; then
            color="warning"
        fi
        
        curl -X POST -H 'Content-type: application/json' \
             --data "{
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"title\": \"AgroTech Deploy [$status]\",
                    \"text\": \"$message\",
                    \"ts\": $(date +%s)
                }]
             }" \
             $WEBHOOK_URL 2>/dev/null || true
    fi
    
    log "NOTIFICAÇÃO [$status]: $message"
}

# Limpar recursos antigos
cleanup() {
    log "Limpando recursos antigos..."
    
    # Remover imagens órfãs
    docker image prune -f
    
    # Remover volumes órfãos
    docker volume prune -f
    
    log_success "Limpeza concluída"
}

# Função principal
main() {
    local start_time=$(date +%s)
    
    log "==================== INÍCIO DO DEPLOY ===================="
    log "Projeto: $PROJECT_NAME"
    log "Ambiente: Produção"
    log "Timestamp: $(date)"
    
    # Executar verificações
    check_dependencies
    check_files
    
    # Fazer backup
    create_backup
    
    # Deploy
    stop_services
    build_images
    start_services
    
    # Verificações pós-deploy
    if health_check && smoke_tests; then
        check_logs
        cleanup
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        send_notification "SUCCESS" "Deploy concluído com sucesso em ${duration}s"
        log_success "==================== DEPLOY CONCLUÍDO ===================="
        log_success "Duração total: ${duration} segundos"
        
        # Mostrar status dos serviços
        log "Status dos serviços:"
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        
    else
        log_error "Deploy falhou nas verificações"
        rollback
        send_notification "ERROR" "Deploy falhou e rollback foi executado"
        exit 1
    fi
}

# Verificar argumentos
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Uso: $0 [opções]"
        echo ""
        echo "Opções:"
        echo "  help          Mostra esta ajuda"
        echo "  check         Apenas verificações, sem deploy"
        echo "  backup        Apenas backup, sem deploy"
        echo "  rollback      Executa rollback manual"
        echo ""
        echo "Variáveis de ambiente:"
        echo "  WEBHOOK_URL   URL para notificações (opcional)"
        echo "  ENV_FILE      Arquivo de ambiente (padrão: .env.prod)"
        exit 0
        ;;
    "check")
        check_dependencies
        check_files
        log_success "Todas as verificações passaram"
        exit 0
        ;;
    "backup")
        create_backup
        exit 0
        ;;
    "rollback")
        rollback
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Argumento inválido: $1"
        echo "Use '$0 help' para ver as opções disponíveis"
        exit 1
        ;;
esac
