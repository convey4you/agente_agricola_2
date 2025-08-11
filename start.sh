#!/bin/bash
echo "🚀 Iniciando Agente Agrícola no Railway..."

# Verificar se é ambiente de produção
if [ "$FLASK_ENV" = "production" ] || [ -n "$DATABASE_URL" ]; then
    echo "🐘 Ambiente de produção detectado - configurando PostgreSQL..."
    
    # Executar migração
    echo "🔄 Executando migração para PostgreSQL..."
    python railway_migrate.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Migração concluída com sucesso"
    else
        echo "⚠️  Migração com avisos - continuando..."
    fi
else
    echo "🔧 Ambiente de desenvolvimento - usando SQLite"
fi

echo "🌐 Iniciando servidor Flask..."
exec python run.py
