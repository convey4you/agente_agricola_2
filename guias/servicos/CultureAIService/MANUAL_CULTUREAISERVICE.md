# MANUAL_CULTUREAISERVICE.md

## Visão Geral
O **CultureAIService** é o serviço de inteligência artificial especializado em análise e recomendações para culturas agrícolas no sistema AgTech Portugal. Ele utiliza modelos de IA e integrações com bases de conhecimento para fornecer sugestões inteligentes, diagnósticos e otimizações específicas para cada tipo de cultura.

## Funcionalidades
- Análise inteligente de dados de culturas
- Recomendações personalizadas para plantio, manejo e colheita
- Diagnóstico de problemas e pragas em culturas
- Integração com bases de conhecimento agrícolas
- Suporte a sugestões contextuais baseadas em clima, solo e localização

## Arquitetura
- **Arquivo principal:** `culture_ai_service.py`
- **Dependências:** CultureService, AIService, base de conhecimento de culturas
- **Padrão:** Service
- **Integração:** AgentService, WeatherDataService, SoilDetectionService

## Modelos e Estruturas
- **CultureAIRequest**: cultura, contexto, dados ambientais
- **CultureAIResponse**: recomendações, score de confiança, justificativas
- **KnowledgeBaseAdapter**: interface para bases de conhecimento

## Métodos Principais
- `analyze_culture(culture: str, context: dict) -> CultureAIResponse`
- `recommend_practices(culture: str, context: dict) -> List[CultureAIResponse]`
- `diagnose_problems(culture: str, symptoms: dict) -> CultureAIResponse`
- `get_knowledge_base_entry(culture: str) -> dict`

## Exemplos de Uso
```python
# Análise de cultura
resp = culture_ai_service.analyze_culture('soja', {'clima': 'úmido', 'solo': 'argiloso'})
print(resp.recomendacoes)

# Diagnóstico de problemas
diag = culture_ai_service.diagnose_problems('milho', {'folhas': 'amareladas'})
print(diag.justificativas)

# Recomendações de práticas
praticas = culture_ai_service.recommend_practices('trigo', {'regiao': 'Alentejo'})
```

## Dependências
- CultureService (dados de culturas)
- AIService (processamento de IA)
- BaseConhecimentoCulturas (base de conhecimento)
- WeatherDataService, SoilDetectionService (contexto ambiental)

## Validações
- Cultura suportada
- Dados ambientais válidos
- Sintomas reconhecidos para diagnóstico

## Segurança
- Controle de acesso a dados sensíveis
- Sanitização de entradas
- Limite de requisições para evitar abuso

## Performance
- Cache de recomendações por cultura
- Processamento assíncrono para análises complexas
- Otimização de consultas à base de conhecimento

## Testes
- Testes unitários para recomendações e diagnósticos
- Testes de integração com CultureService e AIService
- Testes de performance para grandes volumes de dados

## Independência
- Pode ser desacoplado e utilizado em outros sistemas agrícolas
- Interface clara para integração com múltiplas bases de conhecimento
- Não depende de banco de dados próprio

## Conclusão
O CultureAIService potencializa a tomada de decisão agrícola com inteligência artificial especializada, promovendo recomendações precisas, diagnósticos rápidos e integração eficiente com outros módulos do sistema. Sua arquitetura modular garante portabilidade, escalabilidade e fácil manutenção.
