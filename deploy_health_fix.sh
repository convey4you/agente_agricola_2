#!/bin/bash
# Script de Deploy para Railway - Health Check Fix

echo "Iniciando deploy das correcoes de health check..."

# Verificar se estamos na pasta correta
if [ ! -f "app/__init__.py" ]; then
    echo "Erro: Execute este script na raiz do projeto"
    exit 1
fi

# Verificar se health_controller existe
if [ ! -f "app/controllers/health_controller.py" ]; then
    echo "Erro: health_controller.py nao encontrado"
    exit 1
fi

# Verificar registro do blueprint
if ! grep -q "health_bp" app/__init__.py; then
    echo "Erro: health_bp nao esta registrado em app/__init__.py"
    exit 1
fi

echo "Arquivos verificados"

# Fazer deploy
echo "Fazendo commit das mudancas..."
git add .
git commit -m "Fix: Force deploy health check endpoints - Sprint 1 corrections"

echo "Fazendo push para Railway..."
git push origin main

echo "Aguardando deploy..."
sleep 30

echo "Testando endpoints..."
curl -f https://www.agenteagricola.com/health || echo "Health check ainda nao funcionando"

echo "Deploy concluido. Verificar logs com: railway logs"
