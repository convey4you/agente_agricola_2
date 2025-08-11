# 🧹 SCRIPT DE LIMPEZA AUTOMATIZADA DO WORKSPACE AGROTECH
# Versão: 1.0 | Data: 06 de Agosto de 2025
# Execute este script com cuidado e teste após cada seção

param(
    [switch]$DryRun,           # Apenas simula, não remove arquivos
    [switch]$SkipBackup,       # Pula a criação de backup
    [switch]$Verbose           # Exibe mais detalhes
)

# Configurações
$ErrorActionPreference = "Continue"
$startTime = Get-Date
$backupDir = "cleanup_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Contadores para estatísticas
$stats = @{
    TestFiles = 0
    TempFiles = 0
    ReportFiles = 0
    ObsoleteScripts = 0
    CacheDirectories = 0
    TotalFilesRemoved = 0
    TotalSizeFreed = 0
}

Write-Host "🧹 INICIANDO LIMPEZA AUTOMATIZADA DO WORKSPACE AGROTECH" -ForegroundColor Green
Write-Host "📅 Data/Hora: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Cyan
Write-Host "📁 Diretório: $(Get-Location)" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 MODO SIMULAÇÃO ATIVO - Nenhum arquivo será removido!" -ForegroundColor Yellow
}

# ============================================
# FASE 1: BACKUP DE SEGURANÇA
# ============================================

if (-not $SkipBackup -and -not $DryRun) {
    Write-Host "`n📦 FASE 1: Criando backup de segurança..." -ForegroundColor Yellow
    
    try {
        New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
        Write-Host "   ✅ Diretório de backup criado: $backupDir" -ForegroundColor Green
        
        # Backup de arquivos críticos que serão removidos
        $criticalFiles = @(
            "config.py.backup",
            "execute_critical_sql*.py",
            "migrate_*.py"
        )
        
        foreach ($pattern in $criticalFiles) {
            $files = Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                Copy-Item -Path $file -Destination $backupDir -ErrorAction SilentlyContinue
                if ($Verbose) { Write-Host "      📋 Backup: $file" -ForegroundColor Gray }
            }
        }
        
        Write-Host "   ✅ Backup de segurança concluído" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Erro ao criar backup: $_" -ForegroundColor Red
        Write-Host "   🛑 Abortando limpeza por segurança..." -ForegroundColor Red
        exit 1
    }
}

# ============================================
# FASE 2: REMOVER ARQUIVOS DE TESTE
# ============================================

Write-Host "`n🧪 FASE 2: Removendo arquivos de teste..." -ForegroundColor Yellow

# Localizar todos os arquivos de teste
$testFiles = Get-ChildItem -Path . -Recurse -Name "test_*.py" -ErrorAction SilentlyContinue
$testHtmlFiles = Get-ChildItem -Path . -Name "test_*.html" -ErrorAction SilentlyContinue

$totalTestFiles = $testFiles.Count + $testHtmlFiles.Count
Write-Host "   📊 Encontrados $totalTestFiles arquivos de teste" -ForegroundColor Cyan

if ($testFiles.Count -gt 0) {
    foreach ($file in $testFiles) {
        $filePath = $file
        $fileSize = (Get-Item $filePath -ErrorAction SilentlyContinue).Length
        
        if ($DryRun) {
            Write-Host "   [SIMULAÇÃO] Removeria: $file" -ForegroundColor Gray
        } else {
            try {
                Remove-Item -Path $filePath -Force -ErrorAction SilentlyContinue
                $stats.TestFiles++
                $stats.TotalSizeFreed += $fileSize
                if ($Verbose) { Write-Host "      ✅ Removido: $file" -ForegroundColor Green }
            }
            catch {
                Write-Host "      ⚠️ Erro ao remover: $file" -ForegroundColor Yellow
            }
        }
    }
}

if ($testHtmlFiles.Count -gt 0) {
    foreach ($file in $testHtmlFiles) {
        if ($DryRun) {
            Write-Host "   [SIMULAÇÃO] Removeria HTML: $file" -ForegroundColor Gray
        } else {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
            $stats.TestFiles++
        }
    }
}

Write-Host "   ✅ Arquivos de teste processados: $($stats.TestFiles)" -ForegroundColor Green

# ============================================
# FASE 3: REMOVER ARQUIVOS TEMPORÁRIOS
# ============================================

Write-Host "`n📄 FASE 3: Removendo arquivos temporários..." -ForegroundColor Yellow

$tempPatterns = @(
    "temp_*.html",
    "temp_*.py",
    "*.tmp",
    "cookies.txt",
    "cookies_test.txt"
)

foreach ($pattern in $tempPatterns) {
    $tempFiles = Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue
    foreach ($file in $tempFiles) {
        if ($DryRun) {
            Write-Host "   [SIMULAÇÃO] Removeria temp: $file" -ForegroundColor Gray
        } else {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
            $stats.TempFiles++
            if ($Verbose) { Write-Host "      ✅ Removido temp: $file" -ForegroundColor Green }
        }
    }
}

Write-Host "   ✅ Arquivos temporários removidos: $($stats.TempFiles)" -ForegroundColor Green

# ============================================
# FASE 4: REMOVER RELATÓRIOS ANTIGOS
# ============================================

Write-Host "`n📋 FASE 4: Removendo relatórios de validação antigos..." -ForegroundColor Yellow

$reportPatterns = @(
    "validation_report_202508*.json",
    "sprint1_validation_report_*.json",
    "test_report_*.json"
)

foreach ($pattern in $reportPatterns) {
    $reportFiles = Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue
    foreach ($file in $reportFiles) {
        if ($DryRun) {
            Write-Host "   [SIMULAÇÃO] Removeria relatório: $file" -ForegroundColor Gray
        } else {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
            $stats.ReportFiles++
            if ($Verbose) { Write-Host "      ✅ Removido relatório: $file" -ForegroundColor Green }
        }
    }
}

Write-Host "   ✅ Relatórios antigos removidos: $($stats.ReportFiles)" -ForegroundColor Green

# ============================================
# FASE 5: LIMPAR DIRETÓRIOS DE CACHE
# ============================================

Write-Host "`n💾 FASE 5: Limpando diretórios de cache..." -ForegroundColor Yellow

$cacheDirs = @(
    "__pycache__",
    ".pytest_cache", 
    "htmlcov"
)

foreach ($dir in $cacheDirs) {
    if (Test-Path $dir) {
        if ($DryRun) {
            Write-Host "   [SIMULAÇÃO] Removeria diretório: $dir" -ForegroundColor Gray
        } else {
            try {
                Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
                $stats.CacheDirectories++
                Write-Host "      ✅ Removido cache: $dir" -ForegroundColor Green
            }
            catch {
                Write-Host "      ⚠️ Erro ao remover cache: $dir" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host "   ✅ Diretórios de cache limpos: $($stats.CacheDirectories)" -ForegroundColor Green

# ============================================
# FASE 6: REMOVER SCRIPTS OBSOLETOS
# ============================================

Write-Host "`n🔧 FASE 6: Removendo scripts obsoletos..." -ForegroundColor Yellow

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

foreach ($script in $obsoleteScripts) {
    if (Test-Path $script) {
        if ($DryRun) {
            Write-Host "   [SIMULAÇÃO] Removeria script: $script" -ForegroundColor Gray
        } else {
            # Fazer backup antes de remover
            if (-not $SkipBackup) {
                Copy-Item -Path $script -Destination $backupDir -ErrorAction SilentlyContinue
            }
            
            Remove-Item -Path $script -Force -ErrorAction SilentlyContinue
            $stats.ObsoleteScripts++
            Write-Host "      ✅ Removido script: $script" -ForegroundColor Green
        }
    } else {
        if ($Verbose) { Write-Host "      ℹ️ Não encontrado: $script" -ForegroundColor Gray }
    }
}

Write-Host "   ✅ Scripts obsoletos removidos: $($stats.ObsoleteScripts)" -ForegroundColor Green

# ============================================
# FASE 7: REMOVER BANCOS SQLITE OBSOLETOS
# ============================================

Write-Host "`n🗄️ FASE 7: Removendo bancos SQLite obsoletos..." -ForegroundColor Yellow

$sqliteFiles = @(
    "culturas_agricolas.db"
    # Mantemos agente_agricola.db para desenvolvimento local se necessário
)

foreach ($db in $sqliteFiles) {
    if (Test-Path $db) {
        if ($DryRun) {
            Write-Host "   [SIMULAÇÃO] Removeria banco: $db" -ForegroundColor Gray
        } else {
            Remove-Item -Path $db -Force -ErrorAction SilentlyContinue
            Write-Host "      ✅ Removido banco: $db" -ForegroundColor Green
        }
    }
}

# ============================================
# RELATÓRIO FINAL
# ============================================

$endTime = Get-Date
$duration = $endTime - $startTime
$stats.TotalFilesRemoved = $stats.TestFiles + $stats.TempFiles + $stats.ReportFiles + $stats.ObsoleteScripts

Write-Host "`n🎉 LIMPEZA CONCLUÍDA!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n📊 ESTATÍSTICAS:" -ForegroundColor Yellow
Write-Host "   📁 Arquivos de teste removidos: $($stats.TestFiles)" -ForegroundColor White
Write-Host "   🗂️ Arquivos temporários removidos: $($stats.TempFiles)" -ForegroundColor White  
Write-Host "   📋 Relatórios antigos removidos: $($stats.ReportFiles)" -ForegroundColor White
Write-Host "   🔧 Scripts obsoletos removidos: $($stats.ObsoleteScripts)" -ForegroundColor White
Write-Host "   💾 Diretórios de cache limpos: $($stats.CacheDirectories)" -ForegroundColor White
Write-Host "   📊 TOTAL DE ARQUIVOS: $($stats.TotalFilesRemoved)" -ForegroundColor Cyan

if ($stats.TotalSizeFreed -gt 0) {
    $sizeFreedMB = [math]::Round($stats.TotalSizeFreed / 1MB, 2)
    Write-Host "   💽 Espaço liberado: $sizeFreedMB MB" -ForegroundColor Cyan
}

Write-Host "`n⏱️ TEMPO DE EXECUÇÃO:" -ForegroundColor Yellow
Write-Host "   🕐 Duração: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor White

if (-not $DryRun -and -not $SkipBackup) {
    Write-Host "`n📦 BACKUP:" -ForegroundColor Yellow
    Write-Host "   📁 Backup salvo em: $backupDir" -ForegroundColor White
    Write-Host "   ℹ️ Mantenha este backup até confirmar que tudo está funcionando" -ForegroundColor Gray
}

Write-Host "`n🔍 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "   1. ✅ Testar a aplicação: python run.py" -ForegroundColor White
Write-Host "   2. ✅ Verificar funcionalidades críticas" -ForegroundColor White
Write-Host "   3. ✅ Fazer commit das mudanças se tudo estiver OK" -ForegroundColor White
Write-Host "   4. ✅ Deploy teste no Railway" -ForegroundColor White

if ($DryRun) {
    Write-Host "`n🔄 Para executar de verdade, rode sem o parâmetro -DryRun" -ForegroundColor Yellow
}

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎯 WORKSPACE LIMPO E ORGANIZADO!" -ForegroundColor Green
