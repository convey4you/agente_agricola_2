/**
 * Sistema de Onboarding - AgroTech Portugal - CORREÇÃO SPRINT 1
 * Gerenciamento completo do processo de onboarding em 5 etapas
 */

class OnboardingManager {
    constructor() {
        this.currentStep = this.getCurrentStep();
        this.initializeEventListeners();
        this.setupFormValidation();
        console.log('🎯 OnboardingManager inicializado para step', this.currentStep);
    }
    
    getCurrentStep() {
        const urlParams = new URLSearchParams(window.location.search);
        return parseInt(urlParams.get('step')) || 1;
    }
    
    initializeEventListeners() {
        // Event listener para formulário do step 2 - CORREÇÃO SPRINT 1
        const step2Form = document.getElementById('onboardingStep2Form');
        if (step2Form) {
            step2Form.addEventListener('submit', (e) => this.handleStep2Submit(e));
            
            // Validação em tempo real para checkboxes
            const checkboxes = step2Form.querySelectorAll('input[name="interests"]');
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', () => this.validateInterests());
            });
            
            console.log('✅ Event listeners configurados para Step 2');
        }
        
        // Event listeners para outros steps (futuro)
        this.setupNavigationButtons();
    }
    
    setupNavigationButtons() {
        const prevButton = document.querySelector('a[href*="step=1"]');
        if (prevButton) {
            console.log('✅ Botão anterior configurado');
        }
    }
    
    setupFormValidation() {
        // Configurar validação em tempo real
        const requiredFields = document.querySelectorAll('input[required], select[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => {
                if (field.id) {
                    this.clearFieldError(field.id);
                }
            });
        });
        
        console.log(`✅ Validação configurada para ${requiredFields.length} campos obrigatórios`);
    }
    
    async handleStep2Submit(event) {
        event.preventDefault();
        console.log('🚀 Iniciando submissão do Step 2');
        
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        try {
            // 1. Validar formulário
            if (!this.validateStep2Form()) {
                console.log('❌ Validação do formulário falhou');
                return false;
            }
            
            console.log('✅ Validação do formulário passou');
            
            // 2. Mostrar loading state
            this.setLoadingState(submitButton, true);
            
            // 3. Coletar e preparar dados - CORREÇÃO SPRINT 1
            const formData = this.collectFormData(form);
            console.log('📋 Dados coletados:', this.formDataToObject(formData));
            
            // 4. Enviar dados
            const response = await this.submitFormData(formData);
            console.log('📡 Resposta recebida:', response);
            
            // 5. Processar resposta
            if (response.error) {
                console.log('❌ Erro na submissão:', response.error);
                this.handleError(response.error);
            } else {
                console.log('✅ Submissão bem-sucedida');
                this.handleSuccess(response);
            }
            
        } catch (error) {
            console.error('💥 Erro na submissão:', error);
            this.handleError('Erro de conexão. Verifique sua internet e tente novamente.');
        } finally {
            this.setLoadingState(submitButton, false);
        }
    }
    
    validateStep2Form() {
        console.log('🔍 Iniciando validação do formulário Step 2');
        
        let isValid = true;
        const errors = [];
        
        // Validar nome completo - CORREÇÃO SPRINT 1
        const fullName = document.getElementById('full_name').value.trim();
        if (!fullName) {
            errors.push('Nome completo é obrigatório');
            this.setFieldError('full_name', 'Nome completo é obrigatório');
            isValid = false;
        } else if (fullName.length < 2) {
            errors.push('Nome deve ter pelo menos 2 caracteres');
            this.setFieldError('full_name', 'Nome deve ter pelo menos 2 caracteres');
            isValid = false;
        } else {
            this.clearFieldError('full_name');
        }
        
        // Validar telefone (opcional, mas se preenchido deve ser válido)
        const phone = document.getElementById('phone').value.trim();
        if (phone && !this.isValidPortuguesePhone(phone)) {
            errors.push('Formato de telefone inválido');
            this.setFieldError('phone', 'Use um formato válido: +351930461030, 930461030, (11)99999-9999, etc.');
            isValid = false;
        } else {
            this.clearFieldError('phone');
        }
        
        // Validar experiência - CORREÇÃO SPRINT 1
        const farmExperience = document.getElementById('farm_experience').value;
        if (!farmExperience) {
            errors.push('Experiência é obrigatória');
            this.setFieldError('farm_experience', 'Selecione sua experiência');
            isValid = false;
        } else {
            this.clearFieldError('farm_experience');
        }
        
        // Validar tipo de produtor - CORREÇÃO SPRINT 1
        const producerType = document.getElementById('producer_type').value;
        if (!producerType) {
            errors.push('Tipo de produtor é obrigatório');
            this.setFieldError('producer_type', 'Selecione o tipo de produtor');
            isValid = false;
        } else {
            this.clearFieldError('producer_type');
        }
        
        // Validar interesses
        const interestsValid = this.validateInterests();
        if (!interestsValid) {
            isValid = false;
        }
        
        console.log(`🔍 Validação concluída: ${isValid ? 'PASSOU' : 'FALHOU'}`);
        if (!isValid) {
            console.log('❌ Erros encontrados:', errors);
        }
        
        return isValid;
    }
    
    validateInterests() {
        const checkboxes = document.querySelectorAll('input[name="interests"]:checked');
        
        if (checkboxes.length === 0) {
            this.showInterestsError('Selecione pelo menos um interesse');
            return false;
        } else if (checkboxes.length > 3) {
            // Usar modal elegante ao invés de mensagem simples
            this.showInterestLimitModal();
            return false;
        } else {
            this.clearInterestsError();
            return true;
        }
    }
    
    isValidPortuguesePhone(phone) {
        // Aceitar vários formatos: com ou sem código de país
        if (!phone || phone.trim() === '') return true; // Campo opcional
        
        // Remover espaços, parênteses, hífens e sinais de mais
        const cleanPhone = phone.replace(/[\s\(\)\-\+]/g, '');
        
        // Formatos aceitos:
        // 1. Portugal: +351930461030, 351930461030, 930461030
        // 2. Brasil: +5511999999999, 5511999999999, 11999999999
        // 3. Outros países: qualquer número com 8-15 dígitos
        
        // Se tem código de país (começa com dígitos seguidos de número longo)
        if (cleanPhone.length >= 10) {
            // Portugal: código 351 + 9 dígitos
            if (cleanPhone.startsWith('351') && cleanPhone.length === 12) {
                return /^351[9]\d{8}$/.test(cleanPhone);
            }
            // Brasil: código 55 + 2 dígitos área + 8-9 dígitos
            if (cleanPhone.startsWith('55') && (cleanPhone.length === 12 || cleanPhone.length === 13)) {
                return /^55\d{10,11}$/.test(cleanPhone);
            }
            // Outros países: 10-15 dígitos
            if (cleanPhone.length >= 10 && cleanPhone.length <= 15) {
                return /^\d{10,15}$/.test(cleanPhone);
            }
        }
        
        // Formato nacional (sem código de país)
        // Portugal: 9 dígitos começando com 9
        if (cleanPhone.length === 9 && cleanPhone.startsWith('9')) {
            return /^9\d{8}$/.test(cleanPhone);
        }
        // Brasil: 10-11 dígitos (área + número)
        if (cleanPhone.length >= 10 && cleanPhone.length <= 11) {
            return /^\d{10,11}$/.test(cleanPhone);
        }
        
        return false;
    }
    
    collectFormData(form) {
        // CORREÇÃO SPRINT 1: Coletar dados com nomes corretos
        const formData = {
            step: 2,
            full_name: document.getElementById('full_name').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            farm_experience: document.getElementById('farm_experience').value,
            producer_type: document.getElementById('producer_type').value,
            interests: []
        };
        
        // Coletar interesses selecionados
        const interessesCheckboxes = document.querySelectorAll('input[name="interests"]:checked');
        interessesCheckboxes.forEach(checkbox => {
            formData.interests.push(checkbox.value);
        });
        
        return formData;
    }
    
    formDataToObject(formData) {
        // Função auxiliar para logging
        return formData;
    }
    
    async submitFormData(formData) {
        // CORREÇÃO SPRINT 1: URL correta e headers apropriados
        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
        
        // Adicionar token CSRF se disponível
        if (window.csrfToken) {
            headers['X-CSRF-Token'] = window.csrfToken;
            console.log('🔒 Token CSRF adicionado ao header');
        } else {
            console.warn('⚠️ Token CSRF não encontrado!');
        }
        
        const response = await fetch('/auth/onboarding/save', {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin',
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Resposta não é JSON válido');
        }
        
        return await response.json();
    }
    
    handleSuccess(response) {
        // Mostrar mensagem de sucesso
        this.showSuccessMessage(response.message || 'Perfil configurado com sucesso!');
        
        // Aguardar um pouco para UX e redirecionar
        setTimeout(() => {
            // Determinar próximo passo baseado no step atual
            const currentStep = parseInt(document.querySelector('input[name="step"]').value);
            const nextStep = currentStep + 1;
            window.location.href = `/auth/onboarding?step=${nextStep}`;
        }, 1000);
    }
    
    handleError(message) {
        this.showErrorMessage(message);
        
        // Scroll para o topo para mostrar erro
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.textContent = 'Processando...';
            button.disabled = true;
            button.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            button.textContent = 'Próximo';
            button.disabled = false;
            button.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }
    
    validateField(field) {
        // Validação individual de campo
        if (!field || !field.id) {
            console.warn('Campo inválido ou sem ID');
            return false;
        }
        
        if (field.hasAttribute('required') && !field.value.trim()) {
            const label = field.previousElementSibling ? field.previousElementSibling.textContent : 'Campo';
            this.setFieldError(field.id, `${label} é obrigatório`);
            return false;
        }
        
        this.clearFieldError(field.id);
        return true;
    }
    
    setFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (!field) {
            console.warn(`Campo ${fieldId} não encontrado para setFieldError`);
            return;
        }
        
        const formGroup = field.closest('div');
        if (!formGroup) {
            console.warn(`FormGroup não encontrado para campo ${fieldId} em setFieldError`);
            return;
        }
        
        // Remover erro existente
        const existingError = formGroup.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Adicionar novo erro
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error text-red-500 text-sm mt-1';
        errorElement.textContent = message;
        
        formGroup.appendChild(errorElement);
        field.classList.add('border-red-300', 'focus:ring-red-500', 'focus:border-red-500');
        field.classList.remove('border-gray-300', 'focus:ring-green-500', 'focus:border-transparent');
    }
    
    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) {
            console.warn(`Campo ${fieldId} não encontrado`);
            return;
        }
        
        const formGroup = field.closest('div');
        if (!formGroup) {
            console.warn(`FormGroup não encontrado para campo ${fieldId}`);
            return;
        }
        
        const errorElement = formGroup.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
        
        field.classList.remove('border-red-300', 'focus:ring-red-500', 'focus:border-red-500');
        field.classList.add('border-gray-300', 'focus:ring-green-500', 'focus:border-transparent');
    }
    
    showInterestsError(message) {
        const container = document.querySelector('input[name="interests"]').closest('div').parentNode;
        
        // Remover erro existente
        const existingError = container.querySelector('.interests-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Adicionar novo erro
        const errorElement = document.createElement('div');
        errorElement.className = 'interests-error text-red-500 text-sm mt-1';
        errorElement.textContent = message;
        
        container.appendChild(errorElement);
    }
    
    clearInterestsError() {
        const container = document.querySelector('input[name="interests"]').closest('div').parentNode;
        const errorElement = container.querySelector('.interests-error');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type) {
        // Remover mensagem existente
        const existingMessage = document.querySelector('.onboarding-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Criar nova mensagem
        const messageElement = document.createElement('div');
        messageElement.className = `onboarding-message p-4 mb-4 rounded-md ${
            type === 'success' 
                ? 'bg-green-50 border border-green-200 text-green-700' 
                : 'bg-red-50 border border-red-200 text-red-700'
        }`;
        messageElement.textContent = message;
        
        // Inserir no início do container
        const container = document.querySelector('.bg-white.rounded-lg');
        container.insertBefore(messageElement, container.firstChild);
        
        // Auto-remover após 5 segundos se for sucesso
        if (type === 'success') {
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 5000);
        }
    }
    
    // Função para exibir modal elegante de limite de interesses
    showInterestLimitModal() {
        // Verificar se temos a função global disponível (definida no template)
        if (typeof window.showInterestLimitModal === 'function') {
            window.showInterestLimitModal();
        } else {
            // Fallback para buscar e mostrar o modal diretamente
            const modal = document.getElementById('interestLimitModal');
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden';
            } else {
                // Último fallback - mostrar alerta simples se o modal não existir
                console.warn('Modal de limite de interesses não encontrado, usando alert');
                alert('Você pode selecionar no máximo 3 interesses.');
            }
        }
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Inicializando OnboardingManager');
    new OnboardingManager();
});
