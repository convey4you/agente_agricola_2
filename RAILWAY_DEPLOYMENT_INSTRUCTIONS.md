
# 🚀 INSTRUÇÕES PARA DEPLOYMENT NO RAILWAY

## 📋 Migration Criado
- **Arquivo**: migrations/versions/railway_sync_20250802_sync_local_to_railway.py
- **Versão**: railway_sync_20250802
- **Objetivo**: Sincronizar estrutura local com Railway PostgreSQL

## 🔄 Passos para Deploy:

### 1. Commit e Push
```bash
git add .
git commit -m "Migration: Sincronização com Railway - 02/08/2025"
git push origin main
```

### 2. Railway vai executar automaticamente:
- O arquivo `run.py` contém a função `deploy()` que executa migrations
- Railway irá aplicar automaticamente o migration no PostgreSQL
- Todas as tabelas serão criadas/atualizadas conforme necessário

### 3. Verificação:
- Acesse o painel do Railway
- Verifique os logs do deployment
- Confirme que o migration foi aplicado com sucesso

## 📊 Estrutura Sincronizada:
✅ Usuários (users)
✅ Fazendas (farms)  
✅ Culturas (cultures, culture_types)
✅ Atividades (activities)
✅ Alertas (alerts, alert_rules, user_alert_preferences)
✅ Marketplace (marketplace_items)
✅ Conversas (conversations, messages)

## 🔧 Em caso de problemas:
1. Verifique os logs do Railway
2. Confirme que DATABASE_URL está configurada
3. Execute manualmente no Railway console: `python run.py deploy`

## 📝 Notas:
- O banco local SQLite permanece inalterado
- Apenas Railway PostgreSQL será atualizado
- Migration é seguro - não remove dados existentes
