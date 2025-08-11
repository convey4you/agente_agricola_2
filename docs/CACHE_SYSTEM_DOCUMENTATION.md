# Sistema de Cache Redis - Aplicação Agrícola

## Visão Geral

Este documento descreve o sistema de cache robusto implementado na aplicação Flask agrícola, usando Redis como backend principal com fallback em memória.

## Arquitetura

### Componentes Principais

1. **CacheManager** (`app/utils/cache_manager.py`)
   - Gerenciador principal do cache
   - Conectividade Redis com fallback em memória
   - Métricas de hit/miss
   - Health checks

2. **Decorators de Cache**
   - `@cached()` - Decorator principal para funções
   - Configuração flexível de timeout por tipo
   - Invalidação automática

3. **Cache Controller** (`app/controllers/cache_controller.py`)
   - API REST para gerenciamento
   - Estatísticas e monitoramento
   - Invalidação manual

## Configuração

### Variáveis de Ambiente

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password_here

# Cache Settings
CACHE_ENABLED=true
```

### Timeouts por Tipo de Dados

| Tipo | Timeout | Justificativa |
|------|---------|---------------|
| Clima | 30 min | Dados meteorológicos mudam frequentemente |
| IA | 1 hora | Respostas de IA são computacionalmente caras |
| Dashboard | 15 min | Dados agregados que mudam moderadamente |
| Culturas | 24 horas | Dados de culturas são relativamente estáticos |

## Uso nos Services

### Weather Service

```python
from app.utils.cache_manager import cached

@cached(
    timeout=lambda: current_app.config.get('CACHE_TIMEOUT_WEATHER', 1800),
    namespace='weather',
    key_func=lambda location: f"current:{location.get('latitude')}_{location.get('longitude')}"
)
def get_current_weather(location):
    # Implementação do método
    pass

# Invalidação
WeatherService.invalidate_weather_cache(location)
WeatherService.clear_all_weather_cache()
```

### AI Service

```python
# Cache automático baseado no conteúdo da mensagem
def process_message(message: str, context: Dict) -> Dict:
    context_hash = hashlib.md5(json.dumps(context).encode()).hexdigest()[:8]
    cache_key = f"ai_response:{hashlib.md5(message.encode()).hexdigest()[:10]}_{context_hash}"
    
    cached_response = cache.get(cache_key, 'ai')
    if cached_response:
        return cached_response
    
    # Processar e cachear resultado
    pass
```

### Dashboard Service

```python
@cached(
    timeout=lambda: current_app.config.get('CACHE_TIMEOUT_DASHBOARD', 900),
    namespace='dashboard',
    key_func=lambda: f"dashboard_data:user_{current_user.id}"
)
def get_dashboard_data():
    # Implementação
    pass
```

### Culture Service

```python
@cached(
    timeout=lambda: current_app.config.get('CACHE_TIMEOUT_CULTURE', 86400),
    namespace='culture',
    key_func=lambda: f"user_cultures:user_{current_user.id}"
)
def get_user_cultures():
    # Implementação
    pass
```

## API de Gerenciamento

### Endpoints Disponíveis

#### GET /cache/stats
Obter estatísticas do cache
```json
{
  "success": true,
  "data": {
    "hits": 1250,
    "misses": 180,
    "hit_rate": 87.4,
    "errors": 2,
    "fallback_hits": 15,
    "memory_cache_size": 45,
    "redis_connected": true
  }
}
```

#### GET /cache/health
Verificar saúde do sistema
```json
{
  "success": true,
  "data": {
    "cache_enabled": true,
    "redis_connected": true,
    "memory_fallback": true,
    "status": "healthy"
  }
}
```

#### POST /cache/clear
Limpar cache por namespace
```json
{
  "namespace": "weather"  // opcional, sem namespace limpa tudo
}
```

#### POST /cache/invalidate/user
Invalidar cache do usuário atual
```json
{
  "types": ["dashboard", "culture", "ai"]
}
```

#### POST /cache/invalidate/weather
Invalidar cache meteorológico
```json
{
  "location": {
    "latitude": 38.7223,
    "longitude": -9.1393
  }
}
```

## Estratégias de Invalidação

### Invalidação Inteligente

1. **Por Alteração de Dados**
   ```python
   # Quando uma cultura é modificada
   CultureService.invalidate_cache_on_culture_change(culture_id, user_id)
   ```

2. **Por Usuário**
   ```python
   # Limpar cache específico do usuário
   DashboardService.invalidate_user_dashboard_cache(user_id)
   ```

3. **Por Localização**
   ```python
   # Cache meteorológico por coordenadas
   WeatherService.invalidate_weather_cache(location)
   ```

### Invalidação em Cascata

Quando uma cultura é modificada:
1. Cache da cultura específica é invalidado
2. Cache de todas as culturas do usuário é invalidado
3. Cache do dashboard do usuário é invalidado (pois mostra dados de culturas)

## Fallback Strategy

### Cenários de Fallback

1. **Redis Indisponível**
   - Cache em memória (limitado a 1000 itens)
   - Limpeza automática de itens expirados
   - Logs de degradação

2. **Falha de Serialização**
   - Tentativa JSON primeiro
   - Fallback para pickle/base64
   - Último recurso: string

3. **Timeout de Conexão**
   - Timeout de 5 segundos
   - Fallback automático para memória
   - Reconexão automática

## Monitoramento

### Métricas Coletadas

- **Hit Rate**: Taxa de acerto do cache
- **Miss Rate**: Taxa de falha do cache
- **Error Rate**: Taxa de erros de conexão
- **Fallback Usage**: Uso do cache em memória
- **Memory Usage**: Uso de memória do Redis

### Alertas Recomendados

- Hit rate < 70%
- Error rate > 5%
- Redis desconectado
- Cache em memória > 80% da capacidade

## Performance

### Benchmarks Esperados

| Operação | Sem Cache | Com Cache | Melhoria |
|----------|-----------|-----------|----------|
| Dados Climáticos | 2-5s | 10-50ms | 40-500x |
| Resposta IA | 3-10s | 5-20ms | 150-2000x |
| Dashboard | 500ms-2s | 10-100ms | 5-200x |
| Lista Culturas | 100-500ms | 5-50ms | 2-100x |

### Otimizações

1. **Compressão**: Dados grandes são comprimidos
2. **TTL Inteligente**: Timeouts baseados na volatilidade dos dados
3. **Namespace Isolation**: Separação por tipo para limpeza eficiente
4. **Lazy Loading**: Cache populado sob demanda

## Troubleshooting

### Problemas Comuns

1. **Redis Connection Error**
   ```
   Solução: Verificar se Redis está rodando
   docker run -d -p 6379:6379 redis:alpine
   ```

2. **High Memory Usage**
   ```
   Solução: Limpar cache old ou aumentar timeout
   POST /cache/clear
   ```

3. **Low Hit Rate**
   ```
   Solução: Verificar padrões de acesso e ajustar timeouts
   ```

### Debug Mode

```python
# Habilitar logs detalhados
import logging
logging.getLogger('cache_manager').setLevel(logging.DEBUG)
```

## Segurança

### Isolamento por Usuário

- Chaves incluem user_id quando apropriado
- Namespaces separados por tipo de dados
- Validação de permissões antes de invalidação

### Sanitização de Dados

- Chaves são hasheadas se muito longas
- Dados sensíveis não são cacheados
- TTL automático para expiração

## Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

### Production Settings
```python
# config.py
class ProductionConfig(Config):
    CACHE_REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
    CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    CACHE_TIMEOUT_WEATHER = 30 * 60      # 30 minutos
    CACHE_TIMEOUT_AI = 60 * 60           # 1 hora
    CACHE_TIMEOUT_DASHBOARD = 15 * 60    # 15 minutos
    CACHE_TIMEOUT_CULTURE = 24 * 60 * 60 # 24 horas
```

## Extensibilidade

### Adicionando Novos Tipos de Cache

1. **Definir Timeout**
   ```python
   CACHE_TIMEOUT_NEW_TYPE = 3600  # 1 hora
   ```

2. **Criar Service Methods**
   ```python
   @cached(
       timeout=lambda: current_app.config.get('CACHE_TIMEOUT_NEW_TYPE', 3600),
       namespace='new_type',
       key_func=lambda param: f"new_type:{param}"
   )
   def get_new_data(param):
       pass
   ```

3. **Adicionar Invalidação**
   ```python
   def invalidate_new_type_cache(param):
       cache.delete(f"new_type:{param}", 'new_type')
   ```

### Custom Cache Decorators

```python
from app.utils.cache_manager import cache

def cached_by_location(timeout=1800):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(lat, lon, *args, **kwargs):
            key = f"{func.__name__}:lat_{lat}_lon_{lon}"
            result = cache.get(key, 'location')
            if result is None:
                result = func(lat, lon, *args, **kwargs)
                cache.set(key, result, timeout, 'location')
            return result
        return wrapper
    return decorator
```

Este sistema de cache robusto proporciona uma melhoria significativa na performance da aplicação agrícola, especialmente para operações que envolvem APIs externas e processamento de IA, mantendo a consistência dos dados através de estratégias inteligentes de invalidação.
