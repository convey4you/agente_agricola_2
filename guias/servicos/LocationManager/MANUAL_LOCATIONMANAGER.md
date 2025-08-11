# MANUAL_LOCATIONMANAGER.md

## Visão Geral
O **LocationManager** é o serviço responsável pela gestão centralizada de dados de localização no sistema AgTech Portugal. Ele atua como repositório e orquestrador de informações geográficas, facilitando a integração entre serviços que dependem de dados de localização, como GeocodingService, SoilDetectionService e CultureService.

## Funcionalidades
- Cadastro, atualização e remoção de localizações
- Consulta de localizações por ID, nome, coordenadas ou região
- Normalização e validação de dados de localização
- Integração com serviços de geocodificação e detecção de solo
- Suporte a múltiplos tipos de localizações (fazendas, cidades, regiões)

## Arquitetura
- **Arquivo principal:** `location_manager.py`
- **Dependências:** GeocodingService, SoilDetectionService (opcional)
- **Padrão:** Service
- **Banco de dados:** Tabela de localizações (opcional)

## Modelos e Estruturas
- **Location**: id, nome, tipo, latitude, longitude, metadados
- **LocationQuery**: filtros para busca (nome, região, tipo, etc.)

## Métodos Principais
- `add_location(data: dict) -> Location`
- `update_location(id: int, data: dict) -> Location`
- `remove_location(id: int) -> bool`
- `get_location_by_id(id: int) -> Location`
- `find_locations(query: LocationQuery) -> List[Location]`
- `normalize_location(data: dict) -> dict`

## Exemplos de Uso
```python
# Cadastro de nova localização
loc = location_manager.add_location({
    'nome': 'Fazenda Boa Vista',
    'tipo': 'fazenda',
    'latitude': -23.5505,
    'longitude': -46.6333
})

# Consulta por ID
loc = location_manager.get_location_by_id(42)

# Busca por região
locs = location_manager.find_locations({'regiao': 'Alentejo'})
```

## Dependências
- GeocodingService (para normalização e validação)
- SoilDetectionService (para enriquecimento de dados)
- Banco de dados (opcional)

## Validações
- Nome não vazio
- Coordenadas válidas
- Tipo de localização permitido
- Unicidade de localização (nome + coordenadas)

## Segurança
- Controle de acesso para operações de escrita
- Sanitização de entradas
- Logs de alterações

## Performance
- Indexação de buscas por região e coordenadas
- Cache de localizações mais acessadas

## Testes
- Testes unitários para CRUD de localizações
- Testes de integração com GeocodingService
- Testes de validação de dados

## Independência
- Pode ser desacoplado e utilizado em outros sistemas
- Interface clara para integração com outros serviços
- Não depende de provedores externos

## Conclusão
O LocationManager centraliza e padroniza a gestão de localizações, promovendo integração eficiente entre serviços geográficos e agrícolas. Sua arquitetura modular garante portabilidade, escalabilidade e fácil manutenção.
