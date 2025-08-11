# MANUAL_AISERVICEV2.md

## Visão Geral
O **AIServiceV2** é a versão aprimorada do serviço de inteligência artificial do sistema AgTech Portugal. Ele expande as capacidades do AIService, oferecendo funcionalidades avançadas de processamento de linguagem natural, análise de imagens, integração com múltiplos provedores de IA e mecanismos de personalização e aprendizado contínuo.

## Funcionalidades
- Processamento avançado de mensagens de texto (NLP)
- Análise de imagens com modelos customizados
- Integração com múltiplos provedores de IA (OpenAI, HuggingFace, etc.)
- Aprendizado contínuo e personalização por usuário
- Sistema de cache otimizado e adaptativo
- Geração de relatórios de uso e performance

## Arquitetura
- **Arquivo principal:** `ai_service_v2.py`
- **Dependências:** OpenAI API, HuggingFace API, cache manager, base de conhecimento local
- **Padrão:** Service
- **Integração:** AgentService, CultureService, AIService

## Modelos e Estruturas
- **AIRequestV2**: tipo, conteúdo, contexto, preferências do usuário
- **AIResponseV2**: resposta, score de confiança, fonte, metadados
- **ProviderAdapter**: interface para múltiplos provedores
- **UserProfile**: histórico, preferências, métricas de uso

## Métodos Principais
- `process_text_message_v2(message: str, context: dict, user_profile: dict) -> AIResponseV2`
- `analyze_image_v2(image: bytes, context: dict, user_profile: dict) -> AIResponseV2`
- `get_suggestions_v2(context: dict, user_profile: dict) -> List[AIResponseV2]`
- `select_provider(context: dict) -> ProviderAdapter`
- `update_user_profile(user_id: int, feedback: dict)`

## Exemplos de Uso
```python
# Processamento de mensagem de texto avançado
resp = ai_service_v2.process_text_message_v2('Como tratar ferrugem?', {'user_id': 1}, user_profile)
print(resp.resposta, resp.fonte)

# Análise de imagem com modelo customizado
resp = ai_service_v2.analyze_image_v2(open('folha.jpg', 'rb').read(), {'user_id': 1}, user_profile)
print(resp.resposta)

# Sugestões personalizadas
sugestoes = ai_service_v2.get_suggestions_v2({'localizacao': 'Alentejo'}, user_profile)
```

## Dependências
- OpenAI API, HuggingFace API (ou outros provedores)
- Base de conhecimento local
- Cache manager
- Serviços de contexto (AgentService, CultureService)

## Validações
- Mensagens/textos não vazios
- Imagens em formato suportado
- Contexto e perfil do usuário válidos
- Respostas válidas dos provedores externos

## Segurança
- Controle de acesso a múltiplos provedores
- Sanitização de entradas
- Limite de requisições e monitoramento de uso
- Armazenamento seguro de chaves de API

## Performance
- Cache adaptativo por usuário e contexto
- Seleção dinâmica de provedores para otimização
- Processamento assíncrono e balanceamento de carga

## Testes
- Testes unitários para novos fluxos de processamento
- Testes de integração com múltiplos provedores
- Testes de performance e personalização

## Independência
- Pode ser desacoplado e utilizado em outros sistemas de IA
- Interface extensível para novos provedores
- Não depende de banco de dados próprio, mas pode usar perfis de usuário

## Conclusão
O AIServiceV2 eleva o nível de inteligência artificial do sistema, promovendo personalização, flexibilidade e integração com múltiplos provedores. Sua arquitetura modular e adaptativa garante portabilidade, escalabilidade e fácil evolução.
