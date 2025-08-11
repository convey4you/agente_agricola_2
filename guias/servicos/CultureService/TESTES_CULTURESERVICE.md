# Testes — CultureService

Este documento apresenta exemplos de testes unitários e de integração para o `CultureService`, cobrindo os principais fluxos de uso e validação de dados.

---

## 1. Teste de Criação de Cultura
```python
def test_create_culture(db_session):
    service = CultureService()
    data = {'nome': 'Trigo', 'tipo': 'Grão', 'area': 5, 'usuario_id': 1}
    cultura = service.create_culture(data)
    assert cultura.id is not None
    assert cultura.nome == 'Trigo'
```

## 2. Teste de Listagem de Culturas
```python
def test_get_cultures_by_user(db_session):
    service = CultureService()
    culturas = service.get_cultures_by_user(user_id=1)
    assert isinstance(culturas, list)
```

## 3. Teste de Atualização de Cultura
```python
def test_update_culture(db_session):
    service = CultureService()
    data = {'area': 15}
    cultura = service.update_culture(culture_id=2, data=data)
    assert cultura.area == 15
```

## 4. Teste de Remoção de Cultura
```python
def test_delete_culture(db_session):
    service = CultureService()
    resultado = service.delete_culture(culture_id=2)
    assert resultado is True
```

## 5. Teste de Validação de Dados Inválidos
```python
import pytest

def test_create_culture_invalid_data(db_session):
    service = CultureService()
    data = {'nome': '', 'tipo': '', 'area': -1, 'usuario_id': 1}
    with pytest.raises(ValueError):
        service.create_culture(data)
```

---

Consulte o manual para detalhes sobre dependências e integração com o banco de dados.
