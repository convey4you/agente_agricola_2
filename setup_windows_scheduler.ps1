# Script PowerShell para configurar agendamento automático de alertas no Windows
# Execute como Administrador

param(
    [string]$ProjectPath = "C:\agente_agricola_fresh",
    [string]$PythonPath = "python",
    [int]$IntervalMinutes = 30
)

Write-Host "=== CONFIGURADOR DE AGENDAMENTO AUTOMÁTICO ===" -ForegroundColor Green
Write-Host ""

# Verificar se está executando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERRO: Este script deve ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com o botão direito no PowerShell e escolha 'Executar como Administrador'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Configurando agendamento automático de alertas..." -ForegroundColor Cyan
Write-Host "Caminho do projeto: $ProjectPath" -ForegroundColor Gray
Write-Host "Intervalo: a cada $IntervalMinutes minutos" -ForegroundColor Gray
Write-Host ""

try {
    # Verificar se o caminho do projeto existe
    if (-not (Test-Path $ProjectPath)) {
        Write-Host "ERRO: Caminho do projeto não encontrado: $ProjectPath" -ForegroundColor Red
        exit 1
    }

    # Verificar se o script existe
    $ScriptPath = Join-Path $ProjectPath "scheduled_alert_generation.py"
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "ERRO: Script não encontrado: $ScriptPath" -ForegroundColor Red
        exit 1
    }

    # Nome da tarefa
    $TaskName = "AgenteAgricola_AlertasAutomaticos"

    # Verificar se a tarefa já existe
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Host "Tarefa existente encontrada. Removendo..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    # Configurar ação
    $Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "scheduled_alert_generation.py" -WorkingDirectory $ProjectPath

    # Configurar trigger (repetir a cada X minutos)
    $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date
    $Trigger.Repetition = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration ([TimeSpan]::MaxValue)

    # Configurar configurações
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

    # Configurar principal (usuário)
    $Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    # Registrar tarefa
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Geração automática de alertas para o Agente Agrícola"

    Write-Host "✅ Tarefa agendada criada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalhes da configuração:" -ForegroundColor Cyan
    Write-Host "- Nome da tarefa: $TaskName" -ForegroundColor Gray
    Write-Host "- Executa a cada: $IntervalMinutes minutos" -ForegroundColor Gray
    Write-Host "- Script: $ScriptPath" -ForegroundColor Gray
    Write-Host "- Usuário: SYSTEM" -ForegroundColor Gray
    Write-Host ""

    # Testar execução imediata (opcional)
    Write-Host "Deseja testar a execução agora? (s/n): " -NoNewline -ForegroundColor Yellow
    $TestRun = Read-Host
    
    if ($TestRun -eq "s" -or $TestRun -eq "S" -or $TestRun -eq "sim") {
        Write-Host "Executando teste..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        
        Start-Sleep -Seconds 3
        
        # Verificar status
        $Task = Get-ScheduledTask -TaskName $TaskName
        $TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
        
        Write-Host "Status da última execução: $($TaskInfo.LastRunTime)" -ForegroundColor Gray
        Write-Host "Resultado: $($TaskInfo.LastTaskResult)" -ForegroundColor Gray
        
        if ($TaskInfo.LastTaskResult -eq 0) {
            Write-Host "✅ Teste executado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Teste executado, mas verifique os logs em scheduled_alerts.log" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "📋 Comandos úteis:" -ForegroundColor Cyan
    Write-Host "Ver status: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "Executar manualmente: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "Remover tarefa: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "Ver logs: Get-Content '$ProjectPath\scheduled_alerts.log' -Tail 20" -ForegroundColor Gray

} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== CONFIGURAÇÃO CONCLUÍDA ===" -ForegroundColor Green
