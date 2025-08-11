#!/bin/bash

# Script de monitoramento e saúde do sistema AgroTech
# Executa verificações de saúde e coleta métricas

set -euo pipefail

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/health-check.log"
METRICS_FILE="/tmp/agrotech-metrics.prom"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Criar diretório de logs se não existir
mkdir -p "$(dirname "$LOG_FILE")"

# Função para verificar se um serviço está rodando
check_service() {
    local service_name=$1
    local container_name=$2
    
    if docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" ps "$container_name" | grep -q "Up"; then
        success "✓ $service_name está executando"
        return 0
    else
        error "✗ $service_name não está executando"
        return 1
    fi
}

# Função para verificar conectividade HTTP
check_http_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url"); then
        if [ "$response" -eq "$expected_status" ]; then
            success "✓ $name respondendo (HTTP $response)"
            return 0
        else
            error "✗ $name retornou HTTP $response (esperado $expected_status)"
            return 1
        fi
    else
        error "✗ $name não está acessível"
        return 1
    fi
}

# Função para verificar uso de recursos
check_resources() {
    log "Verificando uso de recursos..."
    
    # CPU
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    log "CPU: ${cpu_usage}%"
    
    # Memória
    memory_info=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2}')
    log "Memória: ${memory_info}%"
    
    # Disco
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    log "Disco: ${disk_usage}%"
    
    # Verificar limites críticos
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        warning "CPU usage alto: ${cpu_usage}%"
    fi
    
    if (( $(echo "$memory_info > 85" | bc -l) )); then
        warning "Uso de memória alto: ${memory_info}%"
    fi
    
    if [ "$disk_usage" -gt 90 ]; then
        warning "Uso de disco alto: ${disk_usage}%"
    fi
}

# Função para verificar base de dados
check_database() {
    log "Verificando base de dados PostgreSQL..."
    
    # Verificar conectividade
    if docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        success "✓ PostgreSQL está acessível"
        
        # Verificar número de conexões
        connections=$(docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T db psql -U postgres -d agrotech -t -c "SELECT count(*) FROM pg_stat_activity;" | tr -d ' ')
        log "Conexões ativas: $connections"
        
        # Verificar tamanho da base de dados
        db_size=$(docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T db psql -U postgres -d agrotech -t -c "SELECT pg_size_pretty(pg_database_size('agrotech'));" | tr -d ' ')
        log "Tamanho da BD: $db_size"
        
        return 0
    else
        error "✗ PostgreSQL não está acessível"
        return 1
    fi
}

# Função para verificar Redis
check_redis() {
    log "Verificando Redis cache..."
    
    if docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T redis redis-cli ping | grep -q "PONG"; then
        success "✓ Redis está respondendo"
        
        # Verificar uso de memória
        memory_usage=$(docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T redis redis-cli info memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
        log "Memória Redis: $memory_usage"
        
        # Verificar número de keys
        keys_count=$(docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" exec -T redis redis-cli dbsize | tr -d '\r')
        log "Keys em cache: $keys_count"
        
        return 0
    else
        error "✗ Redis não está respondendo"
        return 1
    fi
}

# Função para verificar aplicação
check_application() {
    log "Verificando aplicação AgroTech..."
    
    # Health check endpoint
    check_http_endpoint "API Health" "http://localhost/api/health"
    
    # Verificar login
    check_http_endpoint "Página de Login" "http://localhost/auth/login"
    
    # Verificar dashboard
    check_http_endpoint "Dashboard" "http://localhost/dashboard"
    
    # Verificar tempo de resposta
    response_time=$(curl -o /dev/null -s -w "%{time_total}" "http://localhost/api/health")
    log "Tempo de resposta da API: ${response_time}s"
    
    if (( $(echo "$response_time > 2.0" | bc -l) )); then
        warning "Tempo de resposta alto: ${response_time}s"
    fi
}

# Função para verificar logs por erros
check_logs() {
    log "Verificando logs por erros recentes..."
    
    local error_count
    error_count=$(docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" logs app --since="5m" 2>/dev/null | grep -i "error\|exception\|critical" | wc -l)
    
    if [ "$error_count" -gt 0 ]; then
        warning "Encontrados $error_count erros nos logs dos últimos 5 minutos"
        
        # Mostrar últimos erros
        log "Últimos erros encontrados:"
        docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" logs app --since="5m" 2>/dev/null | grep -i "error\|exception\|critical" | tail -3
    else
        success "✓ Nenhum erro encontrado nos logs recentes"
    fi
}

# Função para gerar métricas personalizadas
generate_metrics() {
    log "Gerando métricas personalizadas..."
    
    # Limpar arquivo de métricas anterior
    > "$METRICS_FILE"
    
    # Métrica de status dos serviços
    for service in app db redis nginx; do
        if docker-compose -f "$PROJECT_DIR/docker-compose.prod.yml" ps "$service" | grep -q "Up"; then
            echo "agrotech_service_up{service=\"$service\"} 1" >> "$METRICS_FILE"
        else
            echo "agrotech_service_up{service=\"$service\"} 0" >> "$METRICS_FILE"
        fi
    done
    
    # Métrica de usuários ativos (simulada - seria obtida da aplicação)
    active_users=$(shuf -i 10-50 -n 1)  # Simulação
    echo "agrotech_active_users $active_users" >> "$METRICS_FILE"
    
    # Métrica de último backup
    if [ -f "$PROJECT_DIR/backups/latest_backup_info" ]; then
        backup_timestamp=$(cat "$PROJECT_DIR/backups/latest_backup_info" | grep "timestamp" | cut -d: -f2 | tr -d ' ')
        echo "agrotech_last_backup_timestamp $backup_timestamp" >> "$METRICS_FILE"
    fi
    
    # Métrica de resposta da API
    api_response=$(curl -o /dev/null -s -w "%{time_total}" "http://localhost/api/health" || echo "0")
    echo "agrotech_api_response_time $api_response" >> "$METRICS_FILE"
    
    log "Métricas geradas em $METRICS_FILE"
}

# Função para enviar alertas
send_alert() {
    local level=$1
    local message=$2
    local webhook_url=${ALERT_WEBHOOK_URL:-""}
    
    if [ -n "$webhook_url" ]; then
        curl -X POST "$webhook_url" \
            -H "Content-Type: application/json" \
            -d "{\"level\": \"$level\", \"message\": \"$message\", \"timestamp\": \"$(date -Iseconds)\"}" \
            > /dev/null 2>&1 || true
    fi
    
    # Log local do alerta
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ALERT [$level]: $message" >> "$PROJECT_DIR/logs/alerts.log"
}

# Função principal
main() {
    log "=== Iniciando verificação de saúde do sistema AgroTech ==="
    
    local overall_status=0
    
    # Verificar serviços
    check_service "Aplicação" "app" || overall_status=1
    check_service "PostgreSQL" "db" || overall_status=1
    check_service "Redis" "redis" || overall_status=1
    check_service "Nginx" "nginx" || overall_status=1
    
    # Verificar recursos
    check_resources
    
    # Verificar conectividade
    check_database || overall_status=1
    check_redis || overall_status=1
    check_application || overall_status=1
    
    # Verificar logs
    check_logs
    
    # Gerar métricas
    generate_metrics
    
    # Status final
    if [ $overall_status -eq 0 ]; then
        success "=== Sistema está saudável ==="
    else
        error "=== Problemas detectados no sistema ==="
        send_alert "warning" "Health check detectou problemas no sistema AgroTech"
    fi
    
    return $overall_status
}

# Verificar se script está sendo executado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
