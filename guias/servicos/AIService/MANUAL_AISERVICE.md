# MANUAL_AISERVICE.md

## Visão Geral
O **AIService** é o serviço principal de inteligência artificial do sistema AgTech Portugal. Ele centraliza o processamento de linguagem natural, análise de imagens e geração de sugestões contextuais, integrando-se com APIs externas (como OpenAI) e bases de conhecimento locais para fornecer respostas rápidas e inteligentes.

## Funcionalidades
- Processamento de mensagens de texto com IA (NLP)
- Análise de imagens de plantas para diagnóstico
- Geração de sugestões contextuais e recomendações agrícolas
- Sistema de cache para otimização de respostas
- Integração com bases de conhecimento locais e APIs externas

## Arquitetura
- **Arquivo principal:** `ai_service.py`
- **Dependências:** OpenAI API, cache manager, base de conhecimento local
- **Padrão:** Service
- **Integração:** AgentService, CultureService

## Modelos e Estruturas
- **AIRequest**: tipo (texto/imagem), conteúdo, contexto
- **AIResponse**: resposta, score de confiança, metadados
- **CacheEntry**: chave, valor, timestamp

## Métodos Principais
- `process_text_message(message: str, context: dict) -> AIResponse`
- `analyze_image(image: bytes, context: dict) -> AIResponse`
- `get_suggestions(context: dict) -> List[AIResponse]`
- `cache_response(key: str, value: AIResponse)`
- `get_cached_response(key: str) -> Optional[AIResponse]`

## Exemplos de Uso
```python
# Processamento de mensagem de texto
resp = ai_service.process_text_message('Como tratar ferrugem na soja?', {'user_id': 1})
print(resp.resposta)

# Análise de imagem
resp = ai_service.analyze_image(open('folha.jpg', 'rb').read(), {'user_id': 1})
print(resp.resposta)

# Sugestões contextuais
sugestoes = ai_service.get_suggestions({'localizacao': 'Alentejo'})
```

## Dependências
- OpenAI API (ou outro provedor de IA)
- Base de conhecimento local
- Cache manager
- Serviços de contexto (AgentService, CultureService)

## Validações
- Mensagens/textos não vazios
- Imagens em formato suportado
- Contexto mínimo para requisições
- Respostas válidas do provedor externo

## Segurança
- Controle de acesso a APIs externas
- Sanitização de entradas
- Limite de requisições para evitar abuso
- Armazenamento seguro de chaves de API

## Performance
- Cache de respostas frequentes
- Pool de conexões para APIs externas
- Processamento assíncrono de tarefas pesadas

## Testes
- Testes unitários para processamento de texto e imagem
- Testes de integração com OpenAI API
- Testes de performance e cache

## Independência
- Pode ser desacoplado e utilizado em outros sistemas de IA
- Interface clara para integração com múltiplos provedores
- Não depende de banco de dados próprio

## Conclusão
O AIService centraliza a inteligência artificial do sistema, promovendo respostas rápidas, diagnósticos precisos e integração eficiente com outros módulos. Sua arquitetura modular garante portabilidade, escalabilidade e fácil manutenção.
