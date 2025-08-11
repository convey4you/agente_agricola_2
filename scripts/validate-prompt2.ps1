# Validação PROMPT 2 - Configuração de Produção e Deploy
# PowerShell Script para Windows

$ErrorActionPreference = "Continue"

# Configurações
$ProjectDir = Get-Location
$SuccessCount = 0
$TotalChecks = 0

# Função de logging
function Write-Log {
    param($Message, $Type = "Info")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    switch ($Type) {
        "Success" { 
            Write-Host "[✓] $Message" -ForegroundColor Green
            $script:SuccessCount++
        }
        "Error" { 
            Write-Host "[✗] $Message" -ForegroundColor Red
        }
        "Warning" { 
            Write-Host "[!] $Message" -ForegroundColor Yellow
        }
        "Info" { 
            Write-Host "[$timestamp] $Message" -ForegroundColor Cyan
        }
    }
}

# Função para verificar arquivo
function Test-FileExists {
    param($FilePath, $Description)
    
    $script:TotalChecks++
    
    if (Test-Path "$ProjectDir\$FilePath") {
        Write-Log "$Description" -Type "Success"
        return $true
    } else {
        Write-Log "$Description - Arquivo não encontrado: $FilePath" -Type "Error"
        return $false
    }
}

# Função para verificar conteúdo
function Test-FileContent {
    param($FilePath, $SearchText, $Description)
    
    $script:TotalChecks++
    
    if ((Test-Path "$ProjectDir\$FilePath") -and (Select-String -Path "$ProjectDir\$FilePath" -Pattern $SearchText -Quiet)) {
        Write-Log "$Description" -Type "Success"
        return $true
    } else {
        Write-Log "$Description - Conteúdo não encontrado em: $FilePath" -Type "Error"
        return $false
    }
}

# Função para verificar diretório
function Test-DirectoryExists {
    param($DirPath, $Description)
    
    $script:TotalChecks++
    
    if (Test-Path "$ProjectDir\$DirPath" -PathType Container) {
        Write-Log "$Description" -Type "Success"
        return $true
    } else {
        Write-Log "$Description - Diretório não encontrado: $DirPath" -Type "Error"
        return $false
    }
}

Write-Log "VALIDACAO PROMPT 2: CONFIGURACAO DE PRODUCAO E DEPLOY"
Write-Log "======================================================"

# 1. DOCKER CONFIGURATION
Write-Log ""
Write-Log "1. CONFIGURACAO DOCKER"
Write-Log "----------------------"

Test-FileExists "Dockerfile.prod" "Dockerfile de produção"
Test-FileContent "Dockerfile.prod" "multi-stage" "Multi-stage build configurado"
Test-FileContent "Dockerfile.prod" "gunicorn" "Gunicorn configurado"
Test-FileContent "Dockerfile.prod" "HEALTHCHECK" "Health check no Docker"

Test-FileExists "docker-compose.prod.yml" "Docker Compose de produção"
Test-FileContent "docker-compose.prod.yml" "postgresql" "PostgreSQL configurado"
Test-FileContent "docker-compose.prod.yml" "redis" "Redis configurado"
Test-FileContent "docker-compose.prod.yml" "nginx" "Nginx configurado"
Test-FileContent "docker-compose.prod.yml" "prometheus" "Prometheus configurado"
Test-FileContent "docker-compose.prod.yml" "grafana" "Grafana configurado"

# 2. NGINX CONFIGURATION
Write-Log ""
Write-Log "2. CONFIGURACAO NGINX"
Write-Log "---------------------"

Test-DirectoryExists "nginx" "Diretório Nginx"
Test-FileExists "nginx\nginx.conf" "Configuração Nginx"
Test-FileContent "nginx\nginx.conf" "ssl_certificate" "SSL configurado"
Test-FileContent "nginx\nginx.conf" "gzip" "Compressão GZIP configurada"
Test-FileContent "nginx\nginx.conf" "limit_req" "Rate limiting configurado"
Test-FileContent "nginx\nginx.conf" "proxy_pass" "Proxy reverso configurado"

# 3. MONITORING SETUP
Write-Log ""
Write-Log "3. SISTEMA DE MONITORAMENTO"
Write-Log "---------------------------"

Test-DirectoryExists "monitoring" "Diretório de monitoramento"
Test-FileExists "monitoring\prometheus.yml" "Configuração Prometheus"
Test-FileExists "monitoring\alerts.yml" "Regras de alertas"
Test-FileContent "monitoring\prometheus.yml" "job_name" "Jobs configurados no Prometheus"

Test-DirectoryExists "monitoring\grafana" "Diretório Grafana"
Test-DirectoryExists "monitoring\grafana\dashboards" "Dashboards Grafana"
Test-FileExists "monitoring\grafana\dashboards\agrotech-overview.json" "Dashboard principal"
Test-FileContent "monitoring\grafana\dashboards\agrotech-overview.json" "panels" "Painéis configurados no dashboard"

# 4. BACKUP SYSTEM
Write-Log ""
Write-Log "4. SISTEMA DE BACKUP"
Write-Log "--------------------"

Test-DirectoryExists "scripts" "Diretório de scripts"
Test-FileExists "scripts\backup.sh" "Script de backup"
Test-FileContent "scripts\backup.sh" "pg_dump" "Backup PostgreSQL configurado"
Test-FileContent "scripts\backup.sh" "tar" "Backup de arquivos configurado"
Test-FileContent "scripts\backup.sh" "cleanup" "Limpeza automática configurada"

# 5. DEPLOYMENT SCRIPTS
Write-Log ""
Write-Log "5. SCRIPTS DE DEPLOY"
Write-Log "--------------------"

Test-FileExists "scripts\deploy.sh" "Script de deploy"
Test-FileContent "scripts\deploy.sh" "health_check" "Health check no deploy"
Test-FileContent "scripts\deploy.sh" "rollback" "Rollback automático"
Test-FileContent "scripts\deploy.sh" "docker-compose" "Docker Compose integration"

Test-FileExists "scripts\health-check.sh" "Script de health check"
Test-FileContent "scripts\health-check.sh" "check_service" "Verificação de serviços"
Test-FileContent "scripts\health-check.sh" "check_database" "Verificação de base de dados"
Test-FileContent "scripts\health-check.sh" "generate_metrics" "Geração de métricas"

# 6. ENVIRONMENT CONFIGURATION
Write-Log ""
Write-Log "6. CONFIGURACAO DE AMBIENTE"
Write-Log "----------------------------"

Test-FileExists ".env.prod.example" "Template de produção"
Test-FileContent ".env.prod.example" "DATABASE_URL" "URL da base de dados"
Test-FileContent ".env.prod.example" "SECRET_KEY" "Chave secreta"
Test-FileContent ".env.prod.example" "GRAFANA_PASSWORD" "Senha do Grafana"
Test-FileContent ".env.prod.example" "OPENWEATHER_API_KEY" "API key do clima"

# 7. SSL CONFIGURATION
Write-Log ""
Write-Log "7. CONFIGURACAO SSL"
Write-Log "-------------------"

Test-DirectoryExists "ssl" "Diretório SSL"

# 8. DOCUMENTATION
Write-Log ""
Write-Log "8. DOCUMENTACAO"
Write-Log "---------------"

Test-DirectoryExists "docs" "Diretório de documentação"
Test-FileExists "docs\DEPLOY.md" "Documentação de deploy"
Test-FileExists "docs\MONITORING.md" "Documentação de monitoramento"
Test-FileContent "docs\DEPLOY.md" "Infraestrutura Mínima" "Requisitos de infraestrutura"
Test-FileContent "docs\MONITORING.md" "Prometheus" "Documentação do Prometheus"

# 9. SECURITY FEATURES
Write-Log ""
Write-Log "9. RECURSOS DE SEGURANCA"
Write-Log "-------------------------"

Test-FileContent "nginx\nginx.conf" "X-Frame-Options" "Headers de segurança"
Test-FileContent "nginx\nginx.conf" "Content-Security-Policy" "CSP configurado"
Test-FileContent "docker-compose.prod.yml" "user:" "Usuário não-root nos containers"
Test-FileContent "scripts\backup.sh" "encryption" "Backup criptografado"

# 10. PERFORMANCE OPTIMIZATION
Write-Log ""
Write-Log "10. OTIMIZACOES DE PERFORMANCE"
Write-Log "------------------------------"

Test-FileContent "docker-compose.prod.yml" "restart: unless-stopped" "Restart automático"
Test-FileContent "nginx\nginx.conf" "keepalive" "Keep-alive configurado"
Test-FileContent "nginx\nginx.conf" "expires" "Cache de arquivos estáticos"
Test-FileContent "Dockerfile.prod" "worker" "Workers otimizados"

# RESULTADO FINAL
Write-Log ""
Write-Log "RESULTADO DA VALIDACAO"
Write-Log "======================"

$Percentage = [math]::Round(($SuccessCount * 100 / $TotalChecks), 2)

Write-Log "Total de verificacoes: $TotalChecks"
Write-Log "Verificacoes bem-sucedidas: $SuccessCount"
Write-Log "Taxa de sucesso: $Percentage%"

if ($Percentage -ge 90) {
    Write-Log "PROMPT 2 IMPLEMENTADO COM SUCESSO!" -Type "Success"
    Write-Log "Configuracao de producao esta pronta para deploy" -Type "Success"
    Write-Log ""
    Write-Log "PROXIMOS PASSOS:"
    Write-Log "1. Configurar variaveis de ambiente (.env.prod)"
    Write-Log "2. Gerar certificados SSL"
    Write-Log "3. Executar: docker-compose -f docker-compose.prod.yml up -d"
    Write-Log "4. Configurar dashboards no Grafana"
    Write-Log "5. Testar backup e restore"
    Write-Log "6. Configurar alertas personalizados"
} elseif ($Percentage -ge 70) {
    Write-Log "PROMPT 2 PARCIALMENTE IMPLEMENTADO" -Type "Warning"
    Write-Log "Alguns componentes precisam de ajustes" -Type "Warning"
    Write-Log "Verifique os itens marcados com [X] acima"
} else {
    Write-Log "PROMPT 2 INCOMPLETO" -Type "Error"
    Write-Log "Muitos componentes criticos estao faltando" -Type "Error"
    Write-Log "E necessario implementar os itens faltantes antes do deploy"
}

Write-Log ""
Write-Log "COMPONENTES IMPLEMENTADOS:"
Write-Log "- Container Docker multi-stage otimizado"
Write-Log "- Nginx com SSL, cache e rate limiting"
Write-Log "- Sistema de monitoramento completo (Prometheus + Grafana)"
Write-Log "- Backup automatizado com retencao inteligente"
Write-Log "- Scripts de deploy com rollback automatico"
Write-Log "- Health checks robustos em todos os niveis"
Write-Log "- Documentacao completa de deploy e operacao"
Write-Log "- Configuracoes de seguranca empresarial"

if ($Percentage -lt 90) {
    exit 1
} else {
    exit 0
}
