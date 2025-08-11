# 🔧 Correção Simples e Direta - Ciclo da Cultura

## Problema
O sistema está mostrando múltiplas sugestões genéricas (30, 45, 60, 75, 90 dias) em vez de mostrar apenas o ciclo específico da cultura selecionada.

## Solução Simples

Vou modificar diretamente a lógica para:
1. Verificar se temos dados específicos da cultura
2. Se sim, mostrar APENAS o valor específico
3. Se não, mostrar as opções genéricas

### Implementação Direta:

```javascript
function mostrarSugestoesCiclo(tipo) {
    const sugestoesDiv = document.getElementById('sugestoes-ciclo');
    const opcoesDiv = document.getElementById('sugestoes-ciclo-opcoes');
    
    // FIRST: Check for specific culture data
    const dadosEspecificos = sessionStorage.getItem('cultura_ciclo_dias');
    
    if (dadosEspecificos) {
        // Show ONLY the specific cycle
        const dias = parseInt(dadosEspecificos.replace(/\D/g, ''));
        opcoesDiv.innerHTML = `
            <p class="text-xs text-green-600 mb-2">🎯 Ciclo desta cultura:</p>
            <button class="px-3 py-1 bg-green-100 text-green-800 rounded">${dias} dias</button>
        `;
    } else {
        // Show generic suggestions
        const ciclos = ciclosPorTipo[tipo] || [];
        const buttons = ciclos.map(d => `<button class="px-2 py-1 bg-blue-100 text-blue-800 rounded">${d} dias</button>`).join(' ');
        opcoesDiv.innerHTML = `
            <p class="text-xs text-blue-600 mb-2">💡 Sugestões por tipo:</p>
            ${buttons}
        `;
    }
    
    sugestoesDiv.classList.remove('hidden');
}
```

Esta abordagem é:
- ✅ Simples e direta
- ✅ Sem duplicação de texto
- ✅ Prioriza dados específicos
- ✅ Fallback para genéricos
