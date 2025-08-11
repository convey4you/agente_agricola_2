# 🔍 Consultas SQL Úteis - AgTech Portugal

Este arquivo contém consultas SQL práticas para trabalhar com o banco de dados do AgTech.

---

## 👤 Consultas de Usuários

### Listar todos os usuários ativos
```sql
SELECT id, email, nome_completo, cidade, estado, experience_level, 
       data_criacao, onboarding_completed
FROM users 
WHERE ativo = 1
ORDER BY data_criacao DESC;
```

### Buscar usuário por email
```sql
SELECT * FROM users WHERE email = 'francismarquesrosa@gmail.com';
```

### Usuários com localização definida
```sql
SELECT email, nome_completo, latitude, longitude, cidade, estado
FROM users 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
```

---

## 🌱 Consultas de Culturas

### Culturas ativas por usuário
```sql
SELECT c.id, c.nome, c.variedade, c.data_plantio, c.area_plantada, 
       ct.name as tipo_cultura, ct.category,
       u.email as usuario
FROM cultures c
JOIN culture_types ct ON c.culture_type_id = ct.id
JOIN users u ON c.user_id = u.id
WHERE c.active = 1
ORDER BY c.data_plantio DESC;
```

### Resumo de culturas por usuário
```sql
SELECT u.email, u.nome_completo,
       COUNT(c.id) as total_culturas,
       SUM(c.area_plantada) as area_total,
       COUNT(CASE WHEN c.active = 1 THEN 1 END) as culturas_ativas
FROM users u
LEFT JOIN cultures c ON u.id = c.user_id
GROUP BY u.id, u.email, u.nome_completo
ORDER BY total_culturas DESC;
```

### Culturas prontas para colheita (próximas 30 dias)
```sql
SELECT c.nome, c.variedade, c.data_colheita_prevista, 
       julianday(c.data_colheita_prevista) - julianday('now') as dias_restantes,
       u.email as usuario
FROM cultures c
JOIN users u ON c.user_id = u.id
WHERE c.active = 1 
  AND c.data_colheita_prevista IS NOT NULL
  AND julianday(c.data_colheita_prevista) - julianday('now') BETWEEN 0 AND 30
ORDER BY dias_restantes ASC;
```

### Tipos de cultura mais populares
```sql
SELECT ct.name, ct.category, COUNT(c.id) as vezes_plantada
FROM culture_types ct
LEFT JOIN cultures c ON ct.id = c.culture_type_id
GROUP BY ct.id, ct.name, ct.category
ORDER BY vezes_plantada DESC;
```

---

## 🚨 Consultas de Alertas

### Alertas ativos por usuário
```sql
SELECT a.id, a.type, a.priority, a.title, a.message, a.created_at,
       u.email as usuario,
       c.nome as cultura_relacionada
FROM alerts a
JOIN users u ON a.user_id = u.id
LEFT JOIN cultures c ON a.culture_id = c.id
WHERE a.status IN ('pending', 'active', 'sent')
ORDER BY a.priority DESC, a.created_at DESC;
```

### Histórico de alertas por tipo
```sql
SELECT type, priority, 
       COUNT(*) as total,
       COUNT(CASE WHEN read_at IS NOT NULL THEN 1 END) as lidos,
       COUNT(CASE WHEN dismissed_at IS NOT NULL THEN 1 END) as dispensados
FROM alerts
GROUP BY type, priority
ORDER BY type, priority;
```

### Alertas não lidos por usuário
```sql
SELECT u.email, COUNT(a.id) as alertas_nao_lidos
FROM users u
LEFT JOIN alerts a ON u.id = a.user_id 
    AND a.read_at IS NULL 
    AND a.status IN ('pending', 'active', 'sent')
GROUP BY u.id, u.email
HAVING alertas_nao_lidos > 0
ORDER BY alertas_nao_lidos DESC;
```

---

## 🌤️ Consultas Meteorológicas

### Dados climáticos mais recentes por localização
```sql
SELECT location_name, temperature, humidity, wind_speed, condition,
       collected_at, data_quality
FROM weather_data
WHERE is_current = 1
ORDER BY collected_at DESC;
```

### Histórico climático de uma localização
```sql
SELECT location_name, temperature, humidity, condition, collected_at
FROM weather_data
WHERE location_name = 'Lisboa'
ORDER BY collected_at DESC
LIMIT 10;
```

### Localizações ativas para coleta
```sql
SELECT name, latitude, longitude, country, timezone, 
       is_default, created_at
FROM weather_locations
WHERE is_active = 1
ORDER BY is_default DESC, name;
```

### Estatísticas climáticas mensais
```sql
SELECT wl.name as localização, ws.period_date, 
       ws.temp_avg, ws.temp_min, ws.temp_max,
       ws.humidity_avg, ws.total_readings
FROM weather_stats ws
JOIN weather_locations wl ON ws.location_id = wl.id
WHERE ws.period_type = 'monthly'
ORDER BY ws.period_date DESC;
```

---

## 🏠 Consultas de Fazendas

### Fazendas com suas culturas
```sql
SELECT f.name as fazenda, f.area_total, f.city, f.state,
       COUNT(c.id) as total_culturas,
       SUM(c.area_plantada) as area_cultivada,
       u.email as proprietario
FROM farms f
JOIN users u ON f.user_id = u.id
LEFT JOIN cultures c ON f.id = c.farm_id AND c.active = 1
GROUP BY f.id, f.name, f.area_total, f.city, f.state, u.email
ORDER BY total_culturas DESC;
```

---

## ⚙️ Consultas de Preferências

### Preferências de alerta por usuário
```sql
SELECT u.email, uap.alert_type, uap.is_enabled, 
       uap.web_enabled, uap.email_enabled, uap.sms_enabled,
       uap.auto_generation_enabled, uap.auto_frequency
FROM user_alert_preferences uap
JOIN users u ON uap.user_id = u.id
WHERE uap.is_enabled = 1
ORDER BY u.email, uap.alert_type;
```

---

## 📊 Consultas de Relatórios

### Dashboard geral do sistema
```sql
SELECT 
    (SELECT COUNT(*) FROM users WHERE ativo = 1) as usuarios_ativos,
    (SELECT COUNT(*) FROM cultures WHERE active = 1) as culturas_ativas,
    (SELECT COUNT(*) FROM farms WHERE ativo = 1) as fazendas_ativas,
    (SELECT COUNT(*) FROM alerts WHERE status IN ('pending', 'active', 'sent')) as alertas_pendentes,
    (SELECT SUM(area_plantada) FROM cultures WHERE active = 1) as area_total_cultivada,
    (SELECT COUNT(*) FROM weather_data WHERE date(collected_at) = date('now')) as dados_clima_hoje;
```

### Usuários mais ativos (com mais culturas)
```sql
SELECT u.email, u.nome_completo, 
       COUNT(c.id) as total_culturas,
       SUM(c.area_plantada) as area_total,
       MAX(c.created_at) as ultima_cultura_criada
FROM users u
JOIN cultures c ON u.id = c.user_id
WHERE c.active = 1
GROUP BY u.id, u.email, u.nome_completo
ORDER BY total_culturas DESC, area_total DESC;
```

### Atividade por mês (culturas criadas)
```sql
SELECT strftime('%Y-%m', created_at) as mes,
       COUNT(*) as culturas_criadas
FROM cultures
GROUP BY strftime('%Y-%m', created_at)
ORDER BY mes DESC;
```

---

## 🔧 Consultas de Manutenção

### Verificar integridade de relacionamentos
```sql
-- Culturas sem usuário válido
SELECT c.id, c.nome, c.user_id 
FROM cultures c 
LEFT JOIN users u ON c.user_id = u.id 
WHERE u.id IS NULL;

-- Alertas sem usuário válido
SELECT a.id, a.title, a.user_id 
FROM alerts a 
LEFT JOIN users u ON a.user_id = u.id 
WHERE u.id IS NULL;

-- Culturas sem tipo válido
SELECT c.id, c.nome, c.culture_type_id 
FROM cultures c 
LEFT JOIN culture_types ct ON c.culture_type_id = ct.id 
WHERE ct.id IS NULL;
```

### Dados órfãos ou inconsistentes
```sql
-- Fazendas sem proprietário
SELECT f.id, f.name, f.user_id 
FROM farms f 
LEFT JOIN users u ON f.user_id = u.id 
WHERE u.id IS NULL;

-- Preferências de alerta sem usuário
SELECT uap.id, uap.user_id, uap.alert_type 
FROM user_alert_preferences uap 
LEFT JOIN users u ON uap.user_id = u.id 
WHERE u.id IS NULL;
```

### Limpeza de dados antigos
```sql
-- Alertas expirados (mais de 30 dias)
SELECT COUNT(*) as alertas_expirados
FROM alerts 
WHERE created_at < datetime('now', '-30 days')
  AND status IN ('read', 'dismissed');

-- Dados climáticos antigos (mais de 90 dias)
SELECT COUNT(*) as dados_clima_antigos
FROM weather_data 
WHERE collected_at < datetime('now', '-90 days')
  AND is_current = 0;
```

---

## 💡 Dicas de Uso

### Conectar ao banco via Python
```python
import sqlite3
conn = sqlite3.connect('C:/agente_agricola_fresh/instance/agente_agricola.db')
cursor = conn.cursor()

# Executar consulta
cursor.execute("SELECT COUNT(*) FROM users")
result = cursor.fetchone()
print(f"Total de usuários: {result[0]}")

conn.close()
```

### Backup do banco
```bash
# Fazer backup
sqlite3 agente_agricola.db ".backup backup_agente_agricola_$(date +%Y%m%d).db"

# Restaurar backup
sqlite3 agente_agricola.db ".restore backup_agente_agricola_20250807.db"
```

---

**Nota:** Todas as consultas foram testadas com a estrutura atual do banco de dados (Agosto 2025). Adapte conforme necessário para mudanças futuras no esquema.
