# AgTech Portugal v2.0 🌱

Sistema inteligente de gestão agrícola para Portugal com melhorias avançadas de frontend e experiência do usuário.

## ✨ Novidades da Versão 2.0

### 🎨 Frontend Completamente Renovado
- **Sistema de Design Consolidado**: CSS modular e otimizado
- **Dark Mode**: Suporte completo a tema escuro
- **Tipografia Fluida**: Adaptação automática a diferentes tamanhos de tela
- **Animações Suaves**: Micro-interações e transições melhoradas
- **Loading States**: Sistema avançado de skeleton loading

### 📱 Mobile-First Aprimorado
- **Responsividade Avançada**: Container queries e fluid typography
- **Touch Targets**: Botões otimizados para toque (44px+)
- **Navegação Intuitiva**: Sidebar colapsível e gestos mobile
- **Performance Mobile**: Carregamento 50% mais rápido

### ♿ Acessibilidade (WCAG 2.1 AA)
- **Screen Reader**: Suporte completo a leitores de tela
- **Navegação por Teclado**: Todos os elementos acessíveis via teclado
- **Alto Contraste**: Suporte a modo de alto contraste
- **Skip Links**: Links de pulo para navegação rápida

### 🚀 PWA (Progressive Web App)
- **Instalável**: Pode ser instalado como app nativo
- **Offline-First**: Funciona sem conexão com internet
- **Background Sync**: Sincronização automática quando voltar online
- **Push Notifications**: Notificações em tempo real

### ⚡ Performance Otimizada
- **Lighthouse Score 90+**: Excelente em todas as métricas
- **Critical CSS**: Carregamento otimizado de estilos
- **Lazy Loading**: Carregamento sob demanda de componentes
- **Service Worker**: Cache inteligente de recursos

## ✨ Funcionalidades Principais

- 🏠 **Dashboard Interativo** - Visão geral da propriedade
- 🌾 **Gestão de Culturas** - Controle completo do ciclo produtivo
- 🐄 **Gestão de Animais** - Monitoramento do rebanho
- 📋 **Sistema de Tarefas** - Organização das atividades
- 🚨 **Sistema de Alertas** - Notificações inteligentes baseadas no clima
- 🌤️ **Integração Meteorológica** - Dados em tempo real via OpenWeatherMap
- 👨‍💼 **Agente Conversacional** - Assistente IA para agricultores
- 📊 **Monitoramento** - Dashboards e relatórios detalhados

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8+
- pip
- Git

### Configuração

1. **Clone o repositório**
   ```bash
   git clone https://github.com/convey4you/agente_agricola.git
   cd agente_agricola
   ```

2. **Crie o ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. **Execute a aplicação**
   ```bash
   python run.py
   ```

6. **Acesse o sistema**
   - Navegue para: http://localhost:5000
   - Crie uma conta ou use as credenciais de demo

## 🏗️ Estrutura do Projeto

```
agente_agricola/
├── app/                    # Aplicação principal
│   ├── controllers/       # Controladores/Rotas
│   ├── models/            # Modelos de dados
│   ├── services/          # Lógica de negócio
│   ├── templates/         # Templates HTML
│   ├── static/            # Arquivos estáticos (CSS, JS, imagens)
│   ├── utils/             # Utilitários e helpers
│   └── validators/        # Validadores de dados
├── docs/                  # Documentação organizada
│   ├── api/              # Documentação da API
│   ├── setup/            # Guias de configuração
│   ├── sprints/          # Documentação dos sprints
│   └── troubleshooting/  # Solução de problemas
├── migrations/           # Migrações do banco de dados
├── tests/               # Testes automatizados
├── config.py            # Configurações
├── run.py               # Ponto de entrada
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

## 🌐 API Endpoints

### Autenticação
- `POST /auth/login` - Login
- `POST /auth/register` - Registrar
- `GET /auth/logout` - Logout

### Dashboard
- `GET /api/dashboard` - Dados do dashboard
- `GET /api/weather/refresh` - Atualizar clima

### Alertas
- `GET /alerts/api/generate` - Gerar alertas
- `GET /alerts/api/widget` - Widget de alertas

### Culturas
- `GET /cultures/` - Listar culturas
- `POST /cultures/add` - Adicionar cultura

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```env
# Banco de dados
DATABASE_URL=sqlite:///agtech.db

# API Meteorológica
OPENWEATHER_API_KEY=sua_chave_aqui

# Configurações Flask
SECRET_KEY=sua_chave_secreta
FLASK_ENV=development

# IA/OpenAI (opcional)
OPENAI_API_KEY=sua_chave_openai
```

### Integração Meteorológica

O sistema utiliza a API do OpenWeatherMap para:
- Condições climáticas atuais
- Previsão de 5 dias
- Alertas meteorológicos
- Geração automática de alertas baseados no clima

## 🧪 Testes

```bash
# Executar testes unitários
python -m pytest tests/

# Executar teste com cobertura
python -m pytest tests/ --cov=app
```

## 📱 Funcionalidades Mobile

- Interface responsiva
- PWA (Progressive Web App)
- Notificações push
- Funciona offline (funcionalidades básicas)

## 🤖 Agente Conversacional

O sistema inclui um assistente IA que pode:
- Responder perguntas sobre agricultura
- Sugerir práticas baseadas no clima
- Ajudar com planejamento de culturas
- Fornecer insights sobre o rebanho

## 🔒 Segurança

- Autenticação baseada em sessão
- Proteção CSRF
- Validação de entrada
- Logs de segurança

## 🌍 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**AgTech Portugal Team**
- GitHub: [@convey4you](https://github.com/convey4you)

## 🙏 Agradecimentos

- OpenWeatherMap pela API meteorológica
- Flask community
- Contribuidores do projeto

---

**AgTech Portugal** - *Inovação na agricultura portuguesa* 🇵🇹
