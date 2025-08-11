// Teste da nova validação de telefone
function testPhoneValidation() {
    // Simular a classe OnboardingManager
    const onboarding = {
        isValidPortuguesePhone: function(phone) {
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
    };
    
    // Testes
    const testCases = [
        { phone: '+351930461030', expected: true, desc: 'Portugal com +' },
        { phone: '351930461030', expected: true, desc: 'Portugal sem +' },
        { phone: '930461030', expected: true, desc: 'Portugal nacional' },
        { phone: '+351 930 461 030', expected: true, desc: 'Portugal com espaços' },
        { phone: '(11) 99999-9999', expected: true, desc: 'Brasil formatado' },
        { phone: '11999999999', expected: true, desc: 'Brasil limpo' },
        { phone: '', expected: true, desc: 'Vazio (opcional)' },
        { phone: '123', expected: false, desc: 'Muito curto' },
        { phone: 'abc', expected: false, desc: 'Não numérico' }
    ];
    
    console.log('🧪 Testando validação de telefone:');
    testCases.forEach(test => {
        const result = onboarding.isValidPortuguesePhone(test.phone);
        const status = result === test.expected ? '✅' : '❌';
        console.log(`${status} ${test.desc}: "${test.phone}" -> ${result}`);
    });
}

// Executar teste
testPhoneValidation();
