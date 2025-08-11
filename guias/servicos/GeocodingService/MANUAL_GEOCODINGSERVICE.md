# MANUAL_GEOCODINGSERVICE.md

## Visão Geral
O **GeocodingService** é responsável por converter endereços em coordenadas geográficas (latitude/longitude) e vice-versa (geocodificação reversa) no sistema AgTech Portugal. Ele serve como camada de abstração para integrações de localização, facilitando funcionalidades como busca de propriedades, recomendações baseadas em localização e integração com mapas.

## Funcionalidades
- Geocodificação: endereço → coordenadas
- Geocodificação reversa: coordenadas → endereço
- Suporte a múltiplos provedores (Google, OpenStreetMap, etc.)
- Validação e normalização de dados de localização
- Integração com outros serviços (ex: CultureService, LocationManager)

## Arquitetura
- **Arquivo principal:** `geocoding_service.py`
- **Controlador:** `geocoding_controller.py`
- **Rotas:** `/api/geocoding/*`
- **Dependências:** requests, provedores externos de geocoding, LocationManager
- **Padrão:** Service/Controller

## Modelos e Estruturas
- **GeocodingRequest**: endereço ou coordenadas
- **GeocodingResult**: latitude, longitude, endereço formatado, status
- **ProviderAdapter**: interface para provedores externos

## Métodos Principais
- `geocode(address: str) -> GeocodingResult`
- `reverse_geocode(lat: float, lon: float) -> GeocodingResult`
- `validate_location(data: dict) -> bool`
- `get_provider(name: str)`

## Exemplos de Uso
```python
# Geocodificação
result = geocoding_service.geocode('Avenida da Liberdade, Lisboa')
print(result.latitude, result.longitude)

# Geocodificação reversa
result = geocoding_service.reverse_geocode(38.7223, -9.1393)
print(result.address)
```

## Dependências
- requests
- Provedores de geocoding (Google Maps API, Nominatim, etc.)
- LocationManager (opcional)

## Validações
- Endereço não vazio
- Coordenadas válidas (latitude: -90 a 90, longitude: -180 a 180)
- Resposta do provedor válida

## Segurança
- Sanitização de entradas para evitar injeção
- Limite de requisições para evitar abuso
- Armazenamento seguro de chaves de API

## Performance
- Cache de resultados frequentes
- Pool de conexões HTTP
- Fallback automático entre provedores

## Testes
- Testes unitários para geocodificação e reversa
- Testes de integração com provedores reais e mocks
- Testes de validação de dados

## Independência
- O serviço pode ser desacoplado e utilizado em outros sistemas
- Interface de provedores permite fácil substituição
- Não depende de banco de dados próprio

## Conclusão
O GeocodingService centraliza e padroniza operações de localização, promovendo integração eficiente e segura com múltiplos provedores e outros serviços do sistema. Sua arquitetura modular garante portabilidade e fácil manutenção.
