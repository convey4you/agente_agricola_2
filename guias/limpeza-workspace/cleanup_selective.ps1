# Script de Limpeza Seletiva - Remove apenas arquivos da raiz do projeto
# Versao segura que nao mexe em venv/ ou .venv/

param([switch]$DryRun)

Write-Host "🧹 LIMPEZA SELETIVA DO WORKSPACE AGROTECH" -ForegroundColor Green
Write-Host "Foco: Arquivos da raiz do projeto apenas" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "MODO SIMULACAO ATIVO" -ForegroundColor Yellow
}

$removedCount = 0

# FASE 1: Arquivos de teste da raiz (nao dos venv)
Write-Host "`n🧪 Removendo arquivos de teste da raiz..." -ForegroundColor Yellow

$rootTestFiles = Get-ChildItem -Path . -Name "test_*.py" -ErrorAction SilentlyContinue
Write-Host "Encontrados $($rootTestFiles.Count) arquivos de teste na raiz"

foreach ($file in $rootTestFiles) {
    if ($DryRun) {
        Write-Host "  [SIMULACAO] $file" -ForegroundColor Gray
    } else {
        Remove-Item -Path $file -Force
        Write-Host "  ✅ $file" -ForegroundColor Green
        $removedCount++
    }
}

# FASE 2: Arquivos temporarios
Write-Host "`n📄 Removendo arquivos temporarios..." -ForegroundColor Yellow

$tempFiles = @(
    "temp_register_fixed.html",
    "test_climate_detection.html", 
    "test_encoding.html",
    "test_modal.html",
    "cookies.txt",
    "cookies_test.txt"
)

foreach ($file in $tempFiles) {
    if (Test-Path $file) {
        if ($DryRun) {
            Write-Host "  [SIMULACAO] $file" -ForegroundColor Gray
        } else {
            Remove-Item -Path $file -Force
            Write-Host "  ✅ $file" -ForegroundColor Green  
            $removedCount++
        }
    }
}

# FASE 3: Relatorios JSON antigos
Write-Host "`n📋 Removendo relatorios antigos..." -ForegroundColor Yellow

$oldReports = @(
    "validation_report_20250801_143032.json",
    "validation_report_20250801_143358.json",
    "validation_report_20250801_143622.json", 
    "validation_report_20250801_143751.json",
    "validation_report_20250801_145114.json",
    "validation_report_20250801_145836.json",
    "sprint1_validation_report_20250801_150221.json"
)

foreach ($file in $oldReports) {
    if (Test-Path $file) {
        if ($DryRun) {
            Write-Host "  [SIMULACAO] $file" -ForegroundColor Gray
        } else {
            Remove-Item -Path $file -Force
            Write-Host "  ✅ $file" -ForegroundColor Green
            $removedCount++
        }
    }
}

# FASE 4: Scripts obsoletos selecionados
Write-Host "`n🔧 Removendo scripts obsoletos..." -ForegroundColor Yellow

$obsoleteScripts = @(
    "analyze_sqlite.py",           # SQLite nao usado mais
    "fix_alerts_columns.py",       # Correcao ja aplicada
    "fix_datetime_warnings.py",    # Warnings corrigidos
    "check_culture_model.py",      # Modelo funcionando
    "debug_buscar_cultura.py",     # Busca funcionando
    "verificar_banco.py",          # Banco funcionando  
    "verificar_base.py",           # Base funcionando
    "culturas_agricolas.db"        # Banco SQLite obsoleto
)

foreach ($file in $obsoleteScripts) {
    if (Test-Path $file) {
        if ($DryRun) {
            Write-Host "  [SIMULACAO] $file" -ForegroundColor Gray
        } else {
            Remove-Item -Path $file -Force
            Write-Host "  ✅ $file" -ForegroundColor Green
            $removedCount++
        }
    }
}

# FASE 5: Cache da raiz apenas
Write-Host "`n💾 Limpando cache da raiz..." -ForegroundColor Yellow

$cacheItems = @("__pycache__", ".pytest_cache", "htmlcov")

foreach ($item in $cacheItems) {
    if (Test-Path $item) {
        if ($DryRun) {
            Write-Host "  [SIMULACAO] $item/" -ForegroundColor Gray
        } else {
            Remove-Item -Path $item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✅ $item/" -ForegroundColor Green
        }
    }
}

# Relatorio final
Write-Host "`n🎉 LIMPEZA SELETIVA CONCLUIDA!" -ForegroundColor Green

if ($DryRun) {
    Write-Host "Modo simulacao - nenhum arquivo removido" -ForegroundColor Yellow
    Write-Host "Execute sem -DryRun para aplicar as mudancas" -ForegroundColor Cyan
} else {
    Write-Host "Total de arquivos removidos: $removedCount" -ForegroundColor White
    Write-Host "Workspace mais limpo e organizado!" -ForegroundColor Green
}

Write-Host "`n✅ Proximos passos:" -ForegroundColor Yellow
Write-Host "1. Testar aplicacao: python run.py" -ForegroundColor White  
Write-Host "2. Fazer commit das mudancas" -ForegroundColor White
Write-Host "3. Deploy teste se tudo OK" -ForegroundColor White
