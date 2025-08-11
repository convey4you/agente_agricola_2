# Limpeza Automatizada do Workspace AgroTech
# Execute este script com cuidado

param(
    [switch]$DryRun
)

$startTime = Get-Date
$backupDir = "cleanup_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "Iniciando limpeza do workspace..." -ForegroundColor Green

if ($DryRun) {
    Write-Host "MODO SIMULACAO - Nenhum arquivo sera removido!" -ForegroundColor Yellow
}

# Contadores
$removedFiles = 0

# FASE 1: Arquivos de teste
Write-Host "`nFASE 1: Removendo arquivos de teste..." -ForegroundColor Yellow
$testFiles = Get-ChildItem -Path . -Recurse -Name "test_*.py" -ErrorAction SilentlyContinue

Write-Host "Encontrados $($testFiles.Count) arquivos de teste"

if (-not $DryRun) {
    foreach ($file in $testFiles) {
        try {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
            $removedFiles++
        }
        catch {
            Write-Host "Erro ao remover: $file" -ForegroundColor Red
        }
    }
} else {
    foreach ($file in $testFiles) {
        Write-Host "[SIMULACAO] Removeria: $file" -ForegroundColor Gray
    }
}

# FASE 2: Arquivos temporarios
Write-Host "`nFASE 2: Removendo arquivos temporarios..." -ForegroundColor Yellow

$tempFiles = @()
$tempFiles += Get-ChildItem -Path . -Name "temp_*.html" -ErrorAction SilentlyContinue
$tempFiles += Get-ChildItem -Path . -Name "test_*.html" -ErrorAction SilentlyContinue
$tempFiles += Get-ChildItem -Path . -Name "cookies*.txt" -ErrorAction SilentlyContinue

Write-Host "Encontrados $($tempFiles.Count) arquivos temporarios"

if (-not $DryRun) {
    foreach ($file in $tempFiles) {
        try {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
            $removedFiles++
            Write-Host "Removido: $file" -ForegroundColor Green
        }
        catch {
            Write-Host "Erro ao remover: $file" -ForegroundColor Red
        }
    }
} else {
    foreach ($file in $tempFiles) {
        Write-Host "[SIMULACAO] Removeria: $file" -ForegroundColor Gray
    }
}

# FASE 3: Relatorios antigos JSON
Write-Host "`nFASE 3: Removendo relatorios antigos..." -ForegroundColor Yellow

$reportFiles = @()
$reportFiles += Get-ChildItem -Path . -Name "validation_report_202508*.json" -ErrorAction SilentlyContinue
$reportFiles += Get-ChildItem -Path . -Name "sprint1_validation_report_*.json" -ErrorAction SilentlyContinue

Write-Host "Encontrados $($reportFiles.Count) relatorios antigos"

if (-not $DryRun) {
    foreach ($file in $reportFiles) {
        try {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
            $removedFiles++
            Write-Host "Removido: $file" -ForegroundColor Green
        }
        catch {
            Write-Host "Erro ao remover: $file" -ForegroundColor Red
        }
    }
} else {
    foreach ($file in $reportFiles) {
        Write-Host "[SIMULACAO] Removeria: $file" -ForegroundColor Gray
    }
}

# FASE 4: Cache directories
Write-Host "`nFASE 4: Limpando cache..." -ForegroundColor Yellow

$cacheDirs = @("__pycache__", ".pytest_cache", "htmlcov")

foreach ($dir in $cacheDirs) {
    if (Test-Path $dir) {
        if (-not $DryRun) {
            try {
                Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "Removido cache: $dir" -ForegroundColor Green
            }
            catch {
                Write-Host "Erro ao remover cache: $dir" -ForegroundColor Red
            }
        } else {
            Write-Host "[SIMULACAO] Removeria cache: $dir" -ForegroundColor Gray
        }
    }
}

# FASE 5: Scripts obsoletos
Write-Host "`nFASE 5: Removendo scripts obsoletos..." -ForegroundColor Yellow

$obsoleteScripts = @(
    "migrate_add_interesses.py",
    "migrate_production_alerts.py", 
    "migration_add_interesses_column.py",
    "fix_alerts_columns.py",
    "fix_datetime_warnings.py",
    "execute_critical_sql_compatible.py",
    "execute_critical_sql_flask.py",
    "analyze_sqlite.py",
    "check_culture_model.py",
    "check_interests_database.py", 
    "check_railway_deploy.py",
    "debug_buscar_cultura.py",
    "railway_migration_fix.py",
    "verificar_banco.py",
    "verificar_base.py"
)

$foundScripts = 0

foreach ($script in $obsoleteScripts) {
    if (Test-Path $script) {
        $foundScripts++
        if (-not $DryRun) {
            try {
                Remove-Item -Path $script -Force -ErrorAction SilentlyContinue
                $removedFiles++
                Write-Host "Removido script: $script" -ForegroundColor Green
            }
            catch {
                Write-Host "Erro ao remover script: $script" -ForegroundColor Red
            }
        } else {
            Write-Host "[SIMULACAO] Removeria script: $script" -ForegroundColor Gray
        }
    }
}

Write-Host "Encontrados $foundScripts scripts obsoletos"

# FASE 6: Bancos SQLite obsoletos
Write-Host "`nFASE 6: Removendo bancos obsoletos..." -ForegroundColor Yellow

if (Test-Path "culturas_agricolas.db") {
    if (-not $DryRun) {
        try {
            Remove-Item -Path "culturas_agricolas.db" -Force -ErrorAction SilentlyContinue
            Write-Host "Removido banco: culturas_agricolas.db" -ForegroundColor Green
        }
        catch {
            Write-Host "Erro ao remover banco" -ForegroundColor Red
        }
    } else {
        Write-Host "[SIMULACAO] Removeria banco: culturas_agricolas.db" -ForegroundColor Gray
    }
}

# Relatorio final
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "LIMPEZA CONCLUIDA!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan

if (-not $DryRun) {
    Write-Host "Total de arquivos removidos: $removedFiles" -ForegroundColor White
} else {
    Write-Host "Modo simulacao - nenhum arquivo foi removido" -ForegroundColor Yellow
}

Write-Host "Tempo de execucao: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor White

Write-Host "`nProximos passos:" -ForegroundColor Yellow
Write-Host "1. Testar a aplicacao: python run.py" -ForegroundColor White
Write-Host "2. Verificar funcionalidades criticas" -ForegroundColor White
Write-Host "3. Fazer commit das mudancas se OK" -ForegroundColor White

if ($DryRun) {
    Write-Host "`nPara executar de verdade, rode sem -DryRun" -ForegroundColor Yellow
}
