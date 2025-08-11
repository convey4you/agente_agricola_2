# MANUAL_SOILDETECTIONSERVICE.md

## Visão Geral
O **SoilDetectionService** é responsável por detectar o tipo de solo com base em localização geográfica, integrando dados geológicos, climáticos e históricos para fornecer análises precisas e recomendações agrícolas. Ele é fundamental para apoiar decisões sobre plantio, irrigação e manejo de culturas.

## Funcionalidades
- Detecção automática do tipo de solo por coordenadas
- Análise de modificadores climáticos e históricos
- Classificação de tipos de solo (ex: argiloso, arenoso, siltoso, etc.)
- Cálculo de níveis de confiança na detecção
- Integração com GeocodingService e LocationManager
- Suporte a enriquecimento de dados para recomendações agrícolas

## Arquitetura
- **Arquivo principal:** `soil_detection_service.py`
- **Dependências:** GeocodingService, LocationManager, WeatherDataService (opcional)
- **Padrão:** Service
- **Banco de dados:** Tabela de solos (opcional)

## Modelos e Estruturas
- **SoilDetectionRequest**: latitude, longitude, dados opcionais
- **SoilDetectionResult**: tipo de solo, nível de confiança, modificadores, recomendações
- **SoilType**: enumeração dos tipos de solo suportados

## Métodos Principais
- `detect_soil_by_coordinates(lat: float, lon: float) -> SoilDetectionResult`
- `analyze_modifiers(data: dict) -> dict`
- `classify_soil(data: dict) -> SoilType`
- `get_confidence_score(data: dict) -> float`

## Exemplos de Uso
```python
# Detecção de solo por coordenadas
result = soil_detection_service.detect_soil_by_coordinates(-23.5505, -46.6333)
print(result.tipo_solo, result.nivel_confianca)

# Análise de modificadores
modifiers = soil_detection_service.analyze_modifiers({'chuva': 120, 'ph': 6.2})
```

## Dependências
- GeocodingService (para validação de localização)
- LocationManager (para dados de referência)
- WeatherDataService (para modificadores climáticos)
- Banco de dados de solos (opcional)

## Validações
- Coordenadas válidas
- Dados climáticos e geológicos consistentes
- Tipo de solo suportado

## Segurança
- Sanitização de entradas
- Controle de acesso para operações sensíveis
- Logs de consultas e alterações

## Performance
- Cache de resultados por coordenada
- Indexação de solos por região
- Processamento assíncrono para grandes volumes

## Testes
- Testes unitários para detecção e classificação
- Testes de integração com serviços dependentes
- Testes de validação de dados e limites

## Independência
- Pode ser desacoplado e utilizado em outros sistemas agrícolas
- Interface clara para integração com outros serviços
- Não depende de provedores externos obrigatórios

## Conclusão
O SoilDetectionService centraliza a análise e classificação de solos, promovendo decisões agrícolas baseadas em dados e integração eficiente com outros serviços do ecossistema AgTech Portugal. Sua arquitetura modular garante portabilidade, precisão e fácil manutenção.
