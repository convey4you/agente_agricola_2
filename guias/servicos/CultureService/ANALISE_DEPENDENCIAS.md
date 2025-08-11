# Análise de Dependências — CultureService

O `CultureService` depende dos seguintes componentes para funcionar corretamente:

---

## 1. Modelos
- `Culture` (app/models/culture.py): Modelo ORM da cultura.
- `User` (app/models/user.py): Para associação de culturas ao usuário.

## 2. Banco de Dados
- SQLAlchemy: ORM utilizado para persistência dos dados.
- Sessão de banco de dados (gerenciada pelo Flask ou contexto do app).

## 3. Validação
- `culture_validators.py`: Validação de dados de entrada.

## 4. Cache
- Flask-Caching: Utilizado para otimização de consultas e performance.

## 5. Integração com Controller
- `culture_controller.py`: Responsável por expor endpoints REST e orquestrar chamadas ao serviço.

## 6. Wizard de Criação
- `CultureWizardService`: Assistente de criação de culturas, utiliza sessão do usuário.

---

## Observações sobre Independência
- O serviço pode ser adaptado para outros sistemas, desde que as dependências acima sejam satisfeitas.
- Para uso independente, é necessário fornecer implementações equivalentes de modelo, sessão de banco, cache e validação.

Consulte o manual para detalhes de arquitetura e exemplos de uso.
