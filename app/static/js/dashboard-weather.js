/**
 * Sistema de Dados Climáticos para Dashboard
 * Atualizado para usar WeatherDataService
 */

class WeatherDashboard {
    constructor() {
        this.weatherContainer = document.getElementById('weather-info');
        this.lastUpdateTime = null;
        this.updateInterval = 10 * 60 * 1000; // 10 minutos
        this.init();
    }

    init() {
        // Carregar dados iniciais
        this.loadWeatherData();
        
        // Configurar auto-refresh
        this.setupAutoRefresh();
        
        // Configurar evento do botão de refresh
        this.setupRefreshButton();
    }

    setupRefreshButton() {
        const refreshBtn = document.getElementById('refresh-weather-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshWeatherData());
        }
    }

    async loadWeatherData() {
        try {
            this.showLoading();
            
            const response = await fetch('/weather/refresh');
            const result = await response.json();
            
            if (result.success && result.data) {
                this.displayWeatherData(result.data);
                this.lastUpdateTime = new Date();
                console.log('✅ Dados climáticos carregados:', result.data);
            } else {
                this.showError(result.message || 'Falha ao carregar dados climáticos');
            }
        } catch (error) {
            console.error('❌ Erro ao carregar clima:', error);
            this.showError('Erro de conexão');
        }
    }

    async refreshWeatherData() {
        console.log('🔄 Forçando coleta da API e atualizando dados climáticos...');
        
        // Mostrar feedback visual
        const refreshBtn = document.getElementById('refresh-weather-btn');
        let icon = null;
        if (refreshBtn) {
            icon = refreshBtn.querySelector('i');
            if (icon) {
                icon.classList.add('fa-spin');
            }
            refreshBtn.disabled = true;
        }
        
        try {
            // Mostrar loading específico
            this.showLoadingWithMessage('Coletando dados da API...');
            
            // Usar endpoint que força coleta da API
            const response = await fetch('/weather/force-collect');
            const result = await response.json();
            
            if (result.success && result.data) {
                this.displayWeatherData(result.data);
                this.lastUpdateTime = new Date();
                console.log(`✅ Dados atualizados: ${result.collection.message}`);
                
                // Mostrar notificação de sucesso
                this.showSuccessToast(result.collection.message);
            } else {
                console.error('❌ Falha na coleta:', result);
                // Tentar carregar dados existentes como fallback
                await this.loadWeatherData();
            }
        } catch (error) {
            console.error('❌ Erro na atualização forçada:', error);
            // Tentar carregar dados existentes como fallback
            await this.loadWeatherData();
        } finally {
            // Restaurar botão
            if (refreshBtn) {
                refreshBtn.disabled = false;
                if (icon) {
                    icon.classList.remove('fa-spin');
                }
            }
        }
    }

    displayWeatherData(data) {
        if (!this.weatherContainer) return;

        const html = `
            <div class="weather-content">
                <!-- Info Principal -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="weather-icon">
                            ${this.getWeatherIcon(data.condition)}
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-gray-900">
                                ${Math.round(data.temperature)}°C
                            </div>
                            <div class="text-sm text-gray-600">
                                ${data.location_name || 'Local não definido'}
                            </div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm text-gray-500">
                            Sensação térmica
                        </div>
                        <div class="text-lg font-semibold text-gray-700">
                            ${data.feels_like ? Math.round(data.feels_like) + '°C' : 'N/A'}
                        </div>
                    </div>
                </div>

                <!-- Condição Atual -->
                <div class="bg-blue-50 rounded-lg p-3 mb-4">
                    <div class="text-center">
                        <div class="text-sm font-medium text-blue-900 mb-1">
                            ${this.translateCondition(data.condition)}
                        </div>
                        <div class="text-xs text-blue-700">
                            Atualizado: ${this.formatTime(data.collected_at)}
                        </div>
                    </div>
                </div>

                <!-- Detalhes -->
                <div class="grid grid-cols-2 gap-4 text-sm mb-4">
                    <div class="weather-detail">
                        <span class="text-gray-500">💧 Umidade:</span>
                        <span class="font-medium">${data.humidity}%</span>
                    </div>
                    <div class="weather-detail">
                        <span class="text-gray-500">💨 Vento:</span>
                        <span class="font-medium">${data.wind_speed} m/s</span>
                    </div>
                    <div class="weather-detail">
                        <span class="text-gray-500">🌡️ Pressão:</span>
                        <span class="font-medium">${data.pressure} hPa</span>
                    </div>
                    <div class="weather-detail">
                        <span class="text-gray-500">👁️ Visibilidade:</span>
                        <span class="font-medium">${data.visibility ? (data.visibility/1000).toFixed(1) + ' km' : 'N/A'}</span>
                    </div>
                </div>

                <!-- Previsão dos Próximos Dias -->
                ${this.generateForecastSection(data.forecast)}

                <!-- Alerta agrícola se aplicável -->
                ${this.generateAgriculturalAlert(data)}
            </div>
        `;

        this.weatherContainer.innerHTML = html;
    }

    generateAgriculturalAlert(data) {
        const alerts = [];
        
        // Verificar condições críticas para agricultura
        if (data.temperature > 35) {
            alerts.push('🔥 Temperatura muito alta - Considere irrigação extra');
        }
        if (data.temperature < 5) {
            alerts.push('❄️ Risco de geada - Proteja culturas sensíveis');
        }
        if (data.humidity > 85) {
            alerts.push('💧 Umidade alta - Monitorize fungos e doenças');
        }
        if (data.wind_speed > 10) {
            alerts.push('💨 Vento forte - Proteja plantas jovens');
        }

        if (alerts.length === 0) return '';

        return `
            <div class="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <div class="text-xs font-medium text-amber-800 mb-2">
                    ⚠️ Alertas Agrícolas
                </div>
                <div class="space-y-1">
                    ${alerts.map(alert => `
                        <div class="text-xs text-amber-700">${alert}</div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    generateForecastSection(forecast) {
        if (!forecast || !Array.isArray(forecast) || forecast.length === 0) {
            return '';
        }

        const forecastDays = forecast.slice(0, 5); // Máximo 5 dias

        return `
            <div class="bg-gray-50 rounded-lg p-3 mb-4">
                <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <i class="fas fa-calendar-alt mr-2"></i>
                    Previsão dos Próximos Dias
                </h4>
                <div class="grid grid-cols-5 gap-2 text-xs">
                    ${forecastDays.map((day, index) => `
                        <div class="text-center">
                            <div class="text-gray-600 font-medium mb-1">
                                ${this.formatForecastDate(day.date, index)}
                            </div>
                            <div class="text-lg mb-1">
                                <i class="${day.icon} text-blue-500"></i>
                            </div>
                            <div class="text-gray-800 font-semibold">
                                ${Math.round(day.temp_max)}°
                            </div>
                            <div class="text-gray-500">
                                ${Math.round(day.temp_min)}°
                            </div>
                            <div class="text-gray-600 text-xs mt-1">
                                ${day.humidity}%
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="text-xs text-gray-500 mt-2 text-center">
                    Máx/Mín • Umidade
                </div>
            </div>
        `;
    }

    formatForecastDate(dateString, index) {
        if (!dateString) return `+${index + 1}d`;
        
        try {
            const date = new Date(dateString);
            
            if (index === 0) {
                return 'Hoje';
            } else if (index === 1) {
                return 'Amanhã';
            } else {
                return date.toLocaleDateString('pt-PT', {
                    weekday: 'short'
                }).replace('.', '');
            }
        } catch (error) {
            return `+${index + 1}d`;
        }
    }

    getWeatherIcon(condition) {
        const iconMap = {
            'clear': '☀️',
            'sunny': '☀️',
            'partly cloudy': '⛅',
            'cloudy': '☁️',
            'overcast': '☁️',
            'rain': '🌧️',
            'light rain': '🌦️',
            'heavy rain': '⛈️',
            'snow': '❄️',
            'mist': '🌫️',
            'fog': '🌫️',
            'wind': '💨'
        };

        const lowerCondition = condition?.toLowerCase() || '';
        
        // Tentar encontrar correspondência exata
        if (iconMap[lowerCondition]) {
            return iconMap[lowerCondition];
        }
        
        // Tentar correspondência parcial
        for (const [key, icon] of Object.entries(iconMap)) {
            if (lowerCondition.includes(key)) {
                return icon;
            }
        }
        
        return '🌤️'; // Ícone padrão
    }

    translateCondition(condition) {
        const translations = {
            'clear': 'Céu limpo',
            'sunny': 'Ensolarado',
            'partly cloudy': 'Parcialmente nublado',
            'cloudy': 'Nublado',
            'overcast': 'Encoberto',
            'rain': 'Chuva',
            'light rain': 'Chuva fraca',
            'heavy rain': 'Chuva forte',
            'snow': 'Neve',
            'mist': 'Neblina',
            'fog': 'Nevoeiro',
            'wind': 'Ventoso'
        };

        const lowerCondition = condition?.toLowerCase() || '';
        return translations[lowerCondition] || condition || 'Condição desconhecida';
    }

    formatTime(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString('pt-PT', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return 'Data inválida';
        }
    }

    showLoading() {
        if (!this.weatherContainer) return;

        this.weatherContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-spinner fa-spin text-gray-300 text-2xl mb-2"></i>
                <p class="text-gray-500 text-sm">Carregando dados meteorológicos...</p>
            </div>
        `;
    }

    showError(message) {
        if (!this.weatherContainer) return;

        this.weatherContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle text-red-300 text-2xl mb-2"></i>
                <p class="text-red-500 text-sm">${message}</p>
                <button id="retry-weather-btn" class="mt-2 text-xs text-gray-600 hover:text-gray-800">
                    Tentar novamente
                </button>
            </div>
        `;
        
        // Adicionar evento ao botão de retry
        const retryBtn = document.getElementById('retry-weather-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.loadWeatherData());
        }
    }

    showLoadingWithMessage(message) {
        if (!this.weatherContainer) return;

        this.weatherContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-spinner fa-spin text-blue-500 text-2xl mb-2"></i>
                <p class="text-gray-500 text-sm">${message}</p>
            </div>
        `;
    }

    showSuccessToast(message) {
        // Criar elemento de notificação temporário
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm';
        toast.innerHTML = `
            <i class="fas fa-check-circle mr-2"></i>
            ${message}
        `;
        
        document.body.appendChild(toast);
        
        // Remover após 3 segundos
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    setupAutoRefresh() {
        // Auto-refresh a cada 10 minutos
        setInterval(() => {
            if (this.lastUpdateTime) {
                const timeSinceUpdate = Date.now() - this.lastUpdateTime.getTime();
                if (timeSinceUpdate >= this.updateInterval) {
                    console.log('🔄 Auto-refresh dos dados climáticos');
                    this.loadWeatherData();
                }
            }
        }, this.updateInterval);
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que o DOM está pronto
    setTimeout(() => {
        window.weatherDashboard = new WeatherDashboard();
        console.log('✅ Sistema de clima do dashboard inicializado');
    }, 500);
});

// Exportar para uso global
window.WeatherDashboard = WeatherDashboard;
