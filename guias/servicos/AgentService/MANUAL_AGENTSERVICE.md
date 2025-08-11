# MANUAL_AGENTSERVICE.md

## Visão Geral
O **AgentService** é o serviço responsável por gerenciar as operações do agente inteligente do sistema AgTech Portugal. Ele centraliza funcionalidades de chat interativo, análise de imagens de plantas, sugestões contextuais e integração com outros módulos de IA, proporcionando uma experiência personalizada e assistiva ao usuário.

## Funcionalidades
- Processamento de mensagens de chat com IA
- Análise de imagens de plantas para identificação de problemas
- Sugestões de culturas e atividades agrícolas baseadas em contexto e localização
- Obtenção e histórico de conversas do usuário
- Integração com serviços de recomendação e validação

## Arquitetura
- **Arquivo principal:** `agent_service.py`
- **Controlador:** `agent_controller.py`
- **Rotas:** `/agent/*`
- **Dependências:** AIService, CultureService, GeocodingService, session/context manager
- **Padrão:** Service/Controller

## Modelos e Estruturas
- **AgentMessage**: mensagem, remetente, timestamp, contexto
- **ImageAnalysisRequest**: imagem, metadados
- **SuggestionResult**: tipo, conteúdo, score de relevância
- **UserSession**: histórico, preferências, contexto

## Métodos Principais
- `process_message(user_id: int, message: str) -> AgentMessage`
- `analyze_image(user_id: int, image: bytes) -> dict`
- `get_user_conversations(user_id: int) -> List[AgentMessage]`
- `suggest_cultures(location: dict) -> List[SuggestionResult]`
- `recommend_activities(user_id: int, context: dict) -> List[SuggestionResult]`

## Exemplos de Uso
```python
# Processamento de mensagem de chat
response = agent_service.process_message(1, 'Quais culturas plantar em agosto?')
print(response.conteudo)

# Análise de imagem de planta
result = agent_service.analyze_image(1, open('folha.jpg', 'rb').read())
print(result['diagnostico'])

# Sugestão de culturas
sugestoes = agent_service.suggest_cultures({'latitude': -23.5, 'longitude': -46.6})
```

## Dependências
- AIService (processamento de linguagem e imagem)
- CultureService (recomendações agrícolas)
- GeocodingService (contexto de localização)
- Session/context manager

## Validações
- Mensagens não vazias
- Imagens em formato suportado
- Usuário autenticado
- Dados de localização válidos

## Segurança
- Controle de acesso por sessão
- Sanitização de entradas do usuário
- Limite de requisições para evitar abuso
- Logs de interações

## Performance
- Cache de respostas frequentes
- Processamento assíncrono de imagens
- Otimização de consultas de histórico

## Testes
- Testes unitários para processamento de mensagens
- Testes de integração com AIService e CultureService
- Testes de performance para análise de imagens

## Independência
- Pode ser desacoplado e utilizado em outros sistemas assistivos
- Interface clara para integração com outros módulos de IA
- Não depende de banco de dados próprio, mas pode usar session/context manager

## Conclusão
O AgentService centraliza a inteligência assistiva do sistema, promovendo interatividade, personalização e integração eficiente com outros serviços. Sua arquitetura modular garante portabilidade, escalabilidade e fácil manutenção.
