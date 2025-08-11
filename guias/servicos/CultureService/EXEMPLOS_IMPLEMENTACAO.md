# Exemplos de Implementação — CultureService

Este documento apresenta exemplos práticos de uso do `CultureService` no contexto do sistema AgTech Portugal, incluindo chamadas de métodos, integração com controladores e manipulação de dados de culturas.

---

## 1. Instanciando o Serviço
```python
from app.services.culture_service import CultureService
culture_service = CultureService()
```

## 2. Criando uma Nova Cultura
```python
nova_cultura = {
    'nome': 'Milho',
    'tipo': 'Grão',
    'area': 10.5,
    'usuario_id': 1
}
cultura_criada = culture_service.create_culture(nova_cultura)
print(cultura_criada.id)
```

## 3. Listando Culturas do Usuário
```python
culturas = culture_service.get_cultures_by_user(user_id=1)
for cultura in culturas:
    print(cultura.nome)
```

## 4. Atualizando uma Cultura
```python
dados_atualizados = {'area': 12.0}
cultura_atualizada = culture_service.update_culture(culture_id=5, data=dados_atualizados)
print(cultura_atualizada.area)
```

## 5. Removendo uma Cultura
```python
removida = culture_service.delete_culture(culture_id=5)
print(removida)  # True se removido com sucesso
```

## 6. Utilizando o Wizard de Criação
```python
from app.services.culture_service import CultureWizardService
wizard = CultureWizardService(user_id=1)
wizard.start()
wizard.set_step_data('nome', 'Soja')
wizard.set_step_data('area', 20)
finalizada = wizard.finish()
print(finalizada)
```

---

## 7. Integração com Controller (Exemplo de Endpoint Flask)
```python
@blueprint.route('/cultures', methods=['POST'])
def criar_cultura():
    data = request.json
    cultura = culture_service.create_culture(data)
    return jsonify({'id': cultura.id, 'nome': cultura.nome})
```

---

Consulte o manual para detalhes sobre validação, tratamento de erros e dependências.
