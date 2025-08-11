-- Inicialização do banco de dados para produção
-- AgroTech Portugal

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configurações de performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_lock_waits = on;

-- Otimizações específicas para aplicação
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET seq_page_cost = 1;
ALTER SYSTEM SET cpu_tuple_cost = 0.01;
ALTER SYSTEM SET cpu_index_tuple_cost = 0.005;
ALTER SYSTEM SET cpu_operator_cost = 0.0025;

-- Configurações de autovacuum
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '1min';
ALTER SYSTEM SET autovacuum_vacuum_threshold = 50;
ALTER SYSTEM SET autovacuum_analyze_threshold = 50;
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.2;
ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.1;

-- Reload da configuração
SELECT pg_reload_conf();

-- Usuário para monitoramento (apenas leitura)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'monitor') THEN
        CREATE ROLE monitor WITH LOGIN PASSWORD 'monitor_password';
        GRANT CONNECT ON DATABASE agrotech_prod TO monitor;
        GRANT USAGE ON SCHEMA public TO monitor;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitor;
        GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO monitor;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO monitor;
    END IF;
END $$;

-- Função para estatísticas de performance
CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE (
    metric_name TEXT,
    metric_value NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'total_connections'::TEXT, count(*)::NUMERIC FROM pg_stat_activity
    UNION ALL
    SELECT 'active_connections'::TEXT, count(*)::NUMERIC FROM pg_stat_activity WHERE state = 'active'
    UNION ALL
    SELECT 'idle_connections'::TEXT, count(*)::NUMERIC FROM pg_stat_activity WHERE state = 'idle'
    UNION ALL
    SELECT 'database_size_mb'::TEXT, (pg_database_size(current_database()) / 1024 / 1024)::NUMERIC
    UNION ALL
    SELECT 'cache_hit_ratio'::TEXT, 
           (sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)))::NUMERIC
    FROM pg_stat_database WHERE datname = current_database();
END;
$$ LANGUAGE plpgsql;

-- Função para limpeza de sessões antigas
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS INTEGER AS $$
DECLARE
    sessions_killed INTEGER;
BEGIN
    SELECT COUNT(*) INTO sessions_killed
    FROM pg_stat_activity 
    WHERE state = 'idle'
    AND query_start < NOW() - INTERVAL '1 hour';
    
    -- Matar sessões idle há mais de 1 hora
    PERFORM pg_terminate_backend(pid)
    FROM pg_stat_activity 
    WHERE state = 'idle'
    AND query_start < NOW() - INTERVAL '1 hour'
    AND pid <> pg_backend_pid();
    
    RETURN sessions_killed;
END;
$$ LANGUAGE plpgsql;

-- View para monitoramento de performance
CREATE OR REPLACE VIEW performance_monitor AS
SELECT 
    'Database Size (MB)' as metric,
    round((pg_database_size(current_database()) / 1024.0 / 1024.0)::numeric, 2) as value
UNION ALL
SELECT 
    'Active Connections' as metric,
    count(*)::numeric as value
FROM pg_stat_activity 
WHERE state = 'active'
UNION ALL
SELECT 
    'Cache Hit Ratio (%)' as metric,
    round((sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)))::numeric, 2) as value
FROM pg_stat_database 
WHERE datname = current_database()
UNION ALL
SELECT 
    'Slow Queries (>1s)' as metric,
    count(*)::numeric as value
FROM pg_stat_statements 
WHERE mean_exec_time > 1000;

-- Índices para otimização
-- Estes índices serão criados após a migração das tabelas principais

-- Log da inicialização
INSERT INTO public.system_logs (level, message, created_at) 
VALUES ('INFO', 'Database initialized for production', NOW())
ON CONFLICT DO NOTHING;
