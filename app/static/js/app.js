// Estado global da aplicação
let currentUser = null;
let currentSection = 'dashboard';

// Verificar autenticação ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    setupMobileOptimizations();
    checkAuthentication();
    
    // Registrar Service Worker para PWA
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/js/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registrado com sucesso:', registration.scope);
                })
                .catch(error => {
                    console.log('Falha ao registrar Service Worker:', error);
                });
        });
    }
});

// Configuração de otimizações para mobile
function setupMobileOptimizations() {
    // Configurar tema escuro/claro
    setupThemeToggle();
    
    // Configurar navegação mobile
    setupMobileNavigation();
    
    // Configurar animações de entrada
    setupScrollAnimations();
    
    // Configurar dropdowns responsivos
    setupResponsiveDropdowns();
}

// Verificar se o usuário está autenticado
async function checkAuthentication() {
    try {
        const response = await fetch('/api/auth/check');
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = 'login.html';
            return;
        }
        
        currentUser = data.user;
        const userEmailEl = document.getElementById('user-email');
        if (userEmailEl) userEmailEl.textContent = currentUser.email;
        
        const propriedadeNomeEl = document.getElementById('propriedade-nome');
        if (propriedadeNomeEl && currentUser.propriedade_nome) {
            propriedadeNomeEl.textContent = currentUser.propriedade_nome;
        }
        
        // Carregar dados iniciais
        atualizarDados();
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        window.location.href = 'login.html';
    }
}

// Logout
async function logout() {
    try {
        const response = await fetch('/auth/logout', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Limpar qualquer dado local
            localStorage.clear();
            sessionStorage.clear();
            
            // Redirecionar para login
            window.location.href = '/auth/login';
        } else {
            console.error('Erro no logout:', response.statusText);
            // Mesmo com erro, redirecionar para login
            window.location.href = '/auth/login';
        }
    } catch (error) {
        console.error('Erro no logout:', error);
        // Mesmo com erro de rede, redirecionar para login
        window.location.href = '/auth/login';
    }
}

// Navegação entre seções
function mostrarSecao(secao) {
    // Esconder todas as seções
    document.querySelectorAll('.secao').forEach(el => el.classList.add('hidden'));
    
    // Mostrar seção selecionada
    document.getElementById(`secao-${secao}`).classList.remove('hidden');
    
    // Atualizar navegação ativa
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    event.target.closest('.nav-item').classList.add('active');
    
    currentSection = secao;
    
    // Carregar dados específicos da seção
    switch(secao) {
        case 'culturas':
            carregarCulturas();
            break;
        case 'graos':
            carregarGraos();
            break;
        case 'animais':
            carregarAnimais();
            break;
        case 'tarefas':
            carregarTarefas();
            break;
        case 'alertas':
            carregarAlertas();
            break;
    }
}

// Atualizar todos os dados
async function atualizarDados() {
    try {
        await Promise.all([
            carregarDashboard(),
            carregarTarefasHoje(),
            carregarAlertasRecentes()
        ]);
        
        // Atualizar seção atual se não for dashboard
        if (currentSection !== 'dashboard') {
            mostrarSecao(currentSection);
        }
    } catch (error) {
        console.error('Erro ao atualizar dados:', error);
    }
}

// Carregar dados do dashboard
async function carregarDashboard() {
    try {
        const [culturasRes, animaisRes, tarefasRes, alertasRes] = await Promise.all([
            fetch('/api/dashboard/culturas'),
            fetch('/api/dashboard/animais'),
            fetch('/api/dashboard/tarefas'),
            fetch('/api/dashboard/alertas')
        ]);
        
        const culturas = await culturasRes.json();
        const animais = await animaisRes.json();
        const tarefas = await tarefasRes.json();
        const alertas = await alertasRes.json();
        
        document.getElementById('total-culturas').textContent = culturas.total_culturas || 0;
        document.getElementById('total-animais').textContent = animais.total_animais || 0;
        document.getElementById('tarefas-hoje').textContent = tarefas.tarefas_hoje || 0;
        document.getElementById('alertas-ativos').textContent = alertas.alertas_ativos || 0;
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
    }
}

// Carregar tarefas de hoje
async function carregarTarefasHoje() {
    try {
        const response = await fetch('/api/tarefas/hoje');
        const tarefas = await response.json();
        
        const container = document.getElementById('tarefas-hoje-lista');
        
        if (tarefas.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">Nenhuma tarefa para hoje</p>';
            return;
        }
        
        container.innerHTML = tarefas.map(tarefa => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-${getTarefaIcon(tarefa.tipo)} text-blue-500"></i>
                    <div>
                        <p class="font-medium">${tarefa.titulo}</p>
                        <p class="text-sm text-gray-600">${tarefa.cultura_nome || 'Geral'}</p>
                    </div>
                </div>
                <span class="status-badge prioridade-${tarefa.prioridade}">${tarefa.prioridade}</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar tarefas de hoje:', error);
    }
}

// Carregar alertas recentes
async function carregarAlertasRecentes() {
    try {
        const response = await fetch('/api/alertas/recentes');
        const alertas = await response.json();
        
        const container = document.getElementById('alertas-recentes-lista');
        
        if (alertas.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">Nenhum alerta recente</p>';
            return;
        }
        
        container.innerHTML = alertas.map(alerta => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-${getAlertaIcon(alerta.tipo)} text-red-500"></i>
                    <div>
                        <p class="font-medium">${alerta.titulo}</p>
                        <p class="text-sm text-gray-600">${alerta.cultura_nome || 'Geral'}</p>
                    </div>
                </div>
                <span class="status-badge status-${alerta.severidade}">${alerta.severidade}</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar alertas recentes:', error);
    }
}

// Carregar culturas
async function carregarCulturas() {
    try {
        const response = await fetch('/api/culturas');
        const culturas = await response.json();
        
        const container = document.getElementById('culturas-lista');
        
        if (culturas.length === 0) {
            container.innerHTML = '<div class="col-span-full text-center text-gray-500">Nenhuma cultura cadastrada</div>';
            return;
        }
        
        container.innerHTML = culturas.filter(c => c.tipo !== 'grao').map(cultura => `
            <div class="bg-white border rounded-lg p-4 card-hover">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="font-semibold text-lg">${cultura.nome}</h3>
                    <span class="status-badge status-${cultura.status}">${cultura.status}</span>
                </div>
                <div class="space-y-2 text-sm text-gray-600">
                    <p><i class="fas fa-tag mr-2"></i>Tipo: ${cultura.tipo}</p>
                    <p><i class="fas fa-seedling mr-2"></i>Variedade: ${cultura.variedade || 'N/A'}</p>
                    <p><i class="fas fa-calendar mr-2"></i>Plantio: ${formatarData(cultura.data_plantio)}</p>
                    <p><i class="fas fa-map-marker-alt mr-2"></i>Área: ${cultura.area_plantada || 0} m²</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar culturas:', error);
    }
}

// Carregar grãos
async function carregarGraos() {
    try {
        const response = await fetch('/api/culturas');
        const culturas = await response.json();
        
        const graos = culturas.filter(c => c.tipo === 'grao');
        const container = document.getElementById('graos-lista');
        
        if (graos.length === 0) {
            container.innerHTML = '<div class="col-span-full text-center text-gray-500">Nenhum grão cadastrado</div>';
            return;
        }
        
        container.innerHTML = graos.map(grao => `
            <div class="bg-white border rounded-lg p-4 card-hover">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="font-semibold text-lg">${grao.nome}</h3>
                    <span class="status-badge status-${grao.status}">${grao.status}</span>
                </div>
                <div class="space-y-2 text-sm text-gray-600">
                    <p><i class="fas fa-seedling mr-2"></i>Variedade: ${grao.variedade || 'N/A'}</p>
                    <p><i class="fas fa-calendar mr-2"></i>Plantio: ${formatarData(grao.data_plantio)}</p>
                    <p><i class="fas fa-clock mr-2"></i>Ciclo: ${grao.ciclo_dias || 'N/A'} dias</p>
                    <p><i class="fas fa-map-marker-alt mr-2"></i>Área: ${grao.area_plantada || 0} m²</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar grãos:', error);
    }
}

// Carregar animais
async function carregarAnimais() {
    try {
        const response = await fetch('/api/animais');
        const animais = await response.json();
        
        const container = document.getElementById('animais-lista');
        
        if (animais.length === 0) {
            container.innerHTML = '<div class="col-span-full text-center text-gray-500">Nenhum animal cadastrado</div>';
            return;
        }
        
        container.innerHTML = animais.map(animal => `
            <div class="bg-white border rounded-lg p-4 card-hover">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="font-semibold text-lg">${animal.especie}</h3>
                    <span class="status-badge status-${animal.status}">${animal.status}</span>
                </div>
                <div class="space-y-2 text-sm text-gray-600">
                    <p><i class="fas fa-paw mr-2"></i>Raça: ${animal.raca || 'N/A'}</p>
                    <p><i class="fas fa-id-card mr-2"></i>ID: ${animal.identificacao || 'N/A'}</p>
                    <p><i class="fas fa-venus-mars mr-2"></i>Sexo: ${animal.sexo || 'N/A'}</p>
                    <p><i class="fas fa-weight mr-2"></i>Peso: ${animal.peso_atual || 'N/A'} kg</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar animais:', error);
    }
}

// Carregar tarefas
async function carregarTarefas() {
    try {
        const response = await fetch('/api/tarefas');
        const tarefas = await response.json();
        
        const container = document.getElementById('tarefas-lista');
        
        if (tarefas.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">Nenhuma tarefa cadastrada</p>';
            return;
        }
        
        container.innerHTML = tarefas.map(tarefa => `
            <div class="bg-gray-50 rounded-lg p-4 mb-4">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold">${tarefa.titulo}</h3>
                    <div class="flex space-x-2">
                        <span class="status-badge status-${tarefa.status}">${tarefa.status}</span>
                        <span class="status-badge prioridade-${tarefa.prioridade}">${tarefa.prioridade}</span>
                    </div>
                </div>
                <p class="text-gray-600 mb-2">${tarefa.descricao || ''}</p>
                <div class="flex justify-between items-center text-sm text-gray-500">
                    <span><i class="fas fa-calendar mr-1"></i>${formatarData(tarefa.data_prevista)}</span>
                    <span><i class="fas fa-leaf mr-1"></i>${tarefa.cultura_nome || 'Geral'}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar tarefas:', error);
    }
}

// Carregar alertas
async function carregarAlertas() {
    try {
        const response = await fetch('/api/alertas');
        const alertas = await response.json();
        
        const container = document.getElementById('alertas-lista');
        
        if (alertas.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">Nenhum alerta ativo</p>';
            return;
        }
        
        container.innerHTML = alertas.map(alerta => `
            <div class="bg-gray-50 rounded-lg p-4 mb-4">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold">${alerta.titulo}</h3>
                    <span class="status-badge status-${alerta.severidade}">${alerta.severidade}</span>
                </div>
                <p class="text-gray-600 mb-2">${alerta.descricao || ''}</p>
                <div class="flex justify-between items-center text-sm text-gray-500">
                    <span><i class="fas fa-calendar mr-1"></i>${formatarData(alerta.data_deteccao)}</span>
                    <span><i class="fas fa-leaf mr-1"></i>${alerta.cultura_nome || 'Geral'}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar alertas:', error);
    }
}

// Funções auxiliares
function formatarData(dataStr) {
    if (!dataStr) return 'N/A';
    const data = new Date(dataStr);
    return data.toLocaleDateString('pt-BR');
}

function getTarefaIcon(tipo) {
    const icons = {
        'irrigacao': 'tint',
        'adubacao': 'leaf',
        'poda': 'cut',
        'colheita': 'apple-alt',
        'tratamento': 'pills',
        'plantio': 'seedling'
    };
    return icons[tipo] || 'tasks';
}

function getAlertaIcon(tipo) {
    const icons = {
        'praga': 'bug',
        'doenca': 'virus',
        'clima': 'cloud',
        'irrigacao': 'tint',
        'colheita': 'apple-alt'
    };
    return icons[tipo] || 'exclamation-triangle';
}

// Funções para modais
let dadosSugeridosModal = null;
let debounceTimer = null;

function abrirModalCultura() {
    document.getElementById('modalCultura').classList.remove('hidden');
    document.getElementById('modalCultura').classList.add('flex');
    
    // Limpar formulário
    document.getElementById('modal-nome-cultura').value = '';
    document.getElementById('modal-tipo-cultura').value = 'hortalica';
    document.getElementById('modal-variedade').value = '';
    document.getElementById('modal-area').value = '';
    document.getElementById('modal-localizacao').value = '';
    document.getElementById('modal-data-plantio').value = '';
    document.getElementById('modal-data-colheita').value = '';
    document.getElementById('modal-observacoes').value = '';
    
    // Limpar status
    document.getElementById('modal-status-verificacao').classList.add('hidden');
    document.getElementById('modal-dados-sugeridos').classList.add('hidden');
    document.getElementById('modal-resultado').classList.add('hidden');
    
    dadosSugeridosModal = null;
}

function fecharModalCultura() {
    document.getElementById('modalCultura').classList.add('hidden');
    document.getElementById('modalCultura').classList.remove('flex');
}

function debounceVerificarCultura() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        const nome = document.getElementById('modal-nome-cultura').value.trim();
        if (nome.length >= 3) {
            verificarCulturaModal();
        }
    }, 1000);
}

async function verificarCulturaModal() {
    const nome = document.getElementById('modal-nome-cultura').value.trim();
    
    if (!nome || nome.length < 3) {
        return;
    }
    
    // Mostrar loading
    document.getElementById('modal-loading').classList.remove('hidden');
    document.getElementById('modal-status-verificacao').classList.add('hidden');
    document.getElementById('modal-dados-sugeridos').classList.add('hidden');
    
    try {
        const response = await fetch('/api/culturas/verificar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nome: nome })
        });
        
        const data = await response.json();
        
        document.getElementById('modal-loading').classList.add('hidden');
        
        if (data.success) {
            dadosSugeridosModal = data.dados_sugeridos;
            exibirStatusVerificacaoModal(data);
            
            if (data.dados_sugeridos) {
                exibirDadosSugeridosModal(data.dados_sugeridos, nome);
            }
        } else {
            exibirErroModal('Erro ao verificar cultura: ' + data.error);
        }
        
    } catch (error) {
        document.getElementById('modal-loading').classList.add('hidden');
        exibirErroModal('Erro de conexão: ' + error.message);
    }
}

function exibirStatusVerificacaoModal(data) {
    const statusDiv = document.getElementById('modal-status-verificacao');
    const { cultura_existe, fonte, message } = data;
    
    statusDiv.classList.remove('hidden');
    
    if (cultura_existe && fonte === 'base_conhecimento') {
        statusDiv.className = 'mt-3 p-3 rounded-lg bg-green-50 border border-green-200 text-green-800';
        statusDiv.innerHTML = `<i class="fas fa-check-circle mr-2"></i><strong>Cultura Conhecida:</strong> ${message}`;
    } else if (fonte === 'cache_auto' || fonte === 'auto_gerado') {
        statusDiv.className = 'mt-3 p-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-800';
        statusDiv.innerHTML = `<i class="fas fa-robot mr-2"></i><strong>Cultura Auto-Gerada:</strong> ${message}`;
    } else {
        statusDiv.className = 'mt-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200 text-yellow-800';
        statusDiv.innerHTML = `<i class="fas fa-question-circle mr-2"></i><strong>Cultura Nova:</strong> ${message}`;
    }
}

function exibirDadosSugeridosModal(dados, nomeCultura) {
    const section = document.getElementById('modal-dados-sugeridos');
    const content = document.getElementById('modal-conteudo-sugerido');
    
    let html = `<div class="bg-white p-2 rounded border-l-4 border-green-500">
                    <strong>🌱 ${nomeCultura.toUpperCase()}</strong><br>
                    <small class="text-gray-600">Ciclo: ${dados.ciclo_dias || 90} dias</small>
                </div>`;
    
    if (dados.irrigacao) {
        html += `<div class="bg-white p-2 rounded border-l-4 border-blue-500">
                    <strong>💧 Irrigação:</strong> ${dados.irrigacao.frequencia}<br>
                    <small class="text-gray-600">${dados.irrigacao.cuidados}</small>
                 </div>`;
    }
    
    if (dados.cuidados_clima) {
        html += `<div class="bg-white p-2 rounded border-l-4 border-yellow-500">
                    <strong>🌡️ Clima:</strong> ${dados.cuidados_clima.temperatura_ideal}
                 </div>`;
    }
    
    if (dados.pragas_doencas && dados.pragas_doencas.principais) {
        const pragas = dados.pragas_doencas.principais.map(p => p.nome).slice(0, 3).join(', ');
        html += `<div class="bg-white p-2 rounded border-l-4 border-red-500">
                    <strong>🐛 Principais Pragas:</strong> ${pragas}
                 </div>`;
    }
    
    content.innerHTML = html;
    section.classList.remove('hidden');
}

function aplicarDadosSugeridosModal() {
    if (!dadosSugeridosModal) {
        alert('Nenhum dado sugerido disponível');
        return;
    }
    
    // Mapear tipo
    const tipoMapping = {
        'cultura_geral': 'hortalica',
        'hortalica_folhosa': 'hortalica',
        'arvore_frutifera': 'arvore_frutifera',
        'cereal': 'cereal',
        'leguminosa': 'leguminosa'
    };
    
    const tipoSugerido = tipoMapping[dadosSugeridosModal.tipo] || 'hortalica';
    document.getElementById('modal-tipo-cultura').value = tipoSugerido;
    
    // Calcular data de colheita
    const dataPlantio = document.getElementById('modal-data-plantio').value;
    if (dataPlantio && dadosSugeridosModal.ciclo_dias) {
        const plantio = new Date(dataPlantio);
        const colheita = new Date(plantio);
        colheita.setDate(plantio.getDate() + dadosSugeridosModal.ciclo_dias);
        document.getElementById('modal-data-colheita').value = colheita.toISOString().split('T')[0];
    }
    
    // Adicionar às observações
    let observacoes = document.getElementById('modal-observacoes').value;
    const infoIA = [
        `📋 Dados sugeridos automaticamente pelo sistema IA`,
        `⏰ Ciclo estimado: ${dadosSugeridosModal.ciclo_dias} dias`
    ];
    
    if (dadosSugeridosModal.irrigacao) {
        infoIA.push(`💧 Irrigação: ${dadosSugeridosModal.irrigacao.frequencia}`);
        infoIA.push(`🌿 Cuidado: ${dadosSugeridosModal.irrigacao.cuidados}`);
    }
    
    if (observacoes) {
        observacoes += '\n\n' + infoIA.join('\n');
    } else {
        observacoes = infoIA.join('\n');
    }
    
    document.getElementById('modal-observacoes').value = observacoes;
    
    // Feedback visual
    exibirSucessoModal('✅ Dados aplicados com sucesso aos campos do formulário!');
}

async function salvarCulturaModal() {
    const nome = document.getElementById('modal-nome-cultura').value.trim();
    
    if (!nome) {
        exibirErroModal('Nome da cultura é obrigatório!');
        return;
    }
    
    const dadosFormulario = {
        nome: nome,
        tipo: document.getElementById('modal-tipo-cultura').value,
        variedade: document.getElementById('modal-variedade').value,
        area_plantada: document.getElementById('modal-area').value,
        localizacao: document.getElementById('modal-localizacao').value,
        data_plantio: document.getElementById('modal-data-plantio').value,
        data_colheita_prevista: document.getElementById('modal-data-colheita').value,
        observacoes: document.getElementById('modal-observacoes').value
    };
    
    document.getElementById('modal-loading').classList.remove('hidden');
    
    try {
        const response = await fetch('/api/culturas/com-sugestao', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosFormulario)
        });
        
        const data = await response.json();
        
        document.getElementById('modal-loading').classList.add('hidden');
        
        if (data.mensagem) {
            let mensagem = `✅ ${data.mensagem}`;
            if (data.fonte_dados === 'auto_sugerido' || data.fonte_dados === 'auto_gerado') {
                mensagem += `\n🤖 Sistema usou dados gerados automaticamente!`;
            }
            
            exibirSucessoModal(mensagem);
            
            // Recarregar lista de culturas se estiver na seção
            if (currentSection === 'culturas') {
                setTimeout(() => {
                    carregarCulturas();
                }, 1000);
            }
            
            // Fechar modal após sucesso
            setTimeout(() => {
                fecharModalCultura();
            }, 2000);
            
        } else {
            exibirErroModal(data.erro || 'Erro ao salvar cultura');
        }
        
    } catch (error) {
        document.getElementById('modal-loading').classList.add('hidden');
        exibirErroModal('Erro de conexão: ' + error.message);
    }
}

function exibirSucessoModal(mensagem) {
    const resultDiv = document.getElementById('modal-resultado');
    resultDiv.className = 'bg-green-50 border border-green-200 text-green-800 p-4 rounded-lg';
    resultDiv.innerHTML = `<i class="fas fa-check-circle mr-2"></i>${mensagem.replace(/\n/g, '<br>')}`;
    resultDiv.classList.remove('hidden');
}

function exibirErroModal(mensagem) {
    const resultDiv = document.getElementById('modal-resultado');
    resultDiv.className = 'bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg';
    resultDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-2"></i>${mensagem}`;
    resultDiv.classList.remove('hidden');
}

function abrirModalGrao() {
    alert('Modal de grão será implementado');
}

function abrirModalAnimal() {
    alert('Modal de animal será implementado');
}

