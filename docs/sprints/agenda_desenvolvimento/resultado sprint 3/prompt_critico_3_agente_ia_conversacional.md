# 🤖 PROMPT CRÍTICO 3: IMPLEMENTAÇÃO DO AGENTE IA CONVERSACIONAL

**DEPENDÊNCIA:** PROMPT 1 (Autenticação corrigida)  
**PRIORIDADE:** ALTA - 48-72 HORAS  
**OBJETIVO:** Assistente de IA especializado em agricultura familiar portuguesa  
**IMPACTO:** 25% do score total do Sprint 3 + Diferencial competitivo

---

## 🎯 CONTEXTO EXECUTIVO

Você é um desenvolvedor especialista em Flask e IA trabalhando no **diferencial competitivo** do AgroTech Portugal: um **Agente de IA Conversacional** especializado em agricultura familiar portuguesa. Este assistente será o coração da plataforma, oferecendo suporte personalizado aos agricultores em português.

**IMPORTANTE:** Este prompt só deve ser executado **APÓS** a correção do sistema de autenticação (Prompt 1), garantindo que a rota `/agent` seja acessível sem redirecionamento.

### 📊 CONTEXTO DO PROBLEMA

**Situação Atual:**
- ❌ Funcionalidade Agente IA: 0% implementada
- ❌ Rota `/agent` inacessível (redirecionamento para login)
- ❌ Nenhuma interface de chat disponível
- ❌ Sem integração com dados do usuário

**Objetivo Final:**
- ✅ Interface de chat conversacional
- ✅ IA especializada em agricultura familiar
- ✅ Integração com dados das culturas do usuário
- ✅ Histórico de conversas persistente
- ✅ Respostas contextuais em português

---

## 🛠️ ESPECIFICAÇÕES TÉCNICAS

### Ambiente de Desenvolvimento
- **Framework:** Flask 3.1.1 + SQLAlchemy 2.0.41
- **IA:** OpenAI GPT-4 ou Claude (via API)
- **Frontend:** HTML5 + CSS3 + JavaScript (WebSocket opcional)
- **Banco de Dados:** PostgreSQL (Railway)
- **Deploy:** Railway (automático via GitHub)
- **Repositório:** https://github.com/convey4you/agente_agricola

### Ferramentas Obrigatórias
- **VS Code** com GitHub Copilot
- **OpenAI Python SDK** ou **Anthropic SDK**
- **Flask-SocketIO** (opcional para chat em tempo real)

---

## 📋 ESPECIFICAÇÕES FUNCIONAIS

### FUNCIONALIDADES OBRIGATÓRIAS

#### 1. INTERFACE DE CHAT
- [x] **Chat em Tempo Real** - Conversa fluida com o agente
- [x] **Histórico de Mensagens** - Conversas anteriores salvas
- [x] **Indicadores Visuais** - Digitando, enviando, erro
- [x] **Design Responsivo** - Mobile e desktop
- [x] **Sugestões de Perguntas** - Tópicos relevantes

#### 2. INTELIGÊNCIA ARTIFICIAL
- [x] **Especialização Agrícola** - Conhecimento em agricultura familiar
- [x] **Contexto Português** - Focado em Portugal e legislação local
- [x] **Integração de Dados** - Acesso às culturas do usuário
- [x] **Respostas Personalizadas** - Baseadas no perfil do agricultor
- [x] **Multilíngua** - Português como padrão

#### 3. FUNCIONALIDADES AVANÇADAS
- [x] **Recomendações Personalizadas** - Baseadas nas culturas
- [x] **Alertas Inteligentes** - Sugestões proativas
- [x] **Integração Climática** - Conselhos baseados no tempo
- [x] **Base de Conhecimento** - FAQ e artigos especializados
- [x] **Feedback de Qualidade** - Avaliação das respostas

---

## 🗃️ MODELO DE DADOS

### TABELA CONVERSATIONS

```python
# app/models/conversation.py
from datetime import datetime
from app import db

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    # Chaves
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # Agrupa mensagens da mesma sessão
    
    # Conteúdo da conversa
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    
    # Metadados
    message_type = db.Column(db.String(20), default='chat')  # chat, suggestion, alert
    context_data = db.Column(db.JSON)  # Dados das culturas usados na resposta
    
    # Qualidade e feedback
    response_time_ms = db.Column(db.Integer)  # Tempo de resposta da IA
    user_rating = db.Column(db.Integer)  # 1-5 estrelas (opcional)
    user_feedback = db.Column(db.Text)  # Feedback textual
    
    # Controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('conversations', lazy=True))
    
    def __repr__(self):
        return f'<Conversation {self.id} - User {self.user_id}>'
    
    def to_dict(self):
        """Converte para dicionário (útil para APIs)"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat(),
            'user_rating': self.user_rating
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    # Chaves
    id = db.Column(db.String(100), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Metadados da sessão
    title = db.Column(db.String(200))  # Título automático baseado na primeira pergunta
    message_count = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('chat_sessions', lazy=True))
    
    def __repr__(self):
        return f'<ChatSession {self.id} - {self.title}>'
```

### MIGRATION NECESSÁRIA

```python
# migrations/versions/xxx_add_conversations_tables.py
"""Adicionar tabelas de conversas

Revision ID: xxx
Revises: yyy
Create Date: 2025-08-01
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Tabela de sessões de chat
    op.create_table('chat_sessions',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de conversas
    op.create_table('conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('user_message', sa.Text(), nullable=False),
        sa.Column('ai_response', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=True),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('conversations')
    op.drop_table('chat_sessions')
```

---

## 🎮 CONTROLLER E ROTAS

### CONTROLLER PRINCIPAL

```python
# app/agent/routes.py
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models.conversation import Conversation, ChatSession
from app.models.culture import Culture
from app.agent.ai_service import AIService
import uuid
from datetime import datetime
import time

agent = Blueprint('agent', __name__, url_prefix='/agent')

@agent.route('/')
@login_required
def index():
    """Interface principal do agente IA"""
    # Buscar sessões recentes do usuário
    recent_sessions = ChatSession.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).order_by(ChatSession.last_activity.desc()).limit(5).all()
    
    # Estatísticas do usuário para contexto
    user_stats = {
        'total_cultures': Culture.query.filter_by(user_id=current_user.id).count(),
        'active_cultures': Culture.query.filter_by(user_id=current_user.id, status='active').count(),
        'total_conversations': Conversation.query.filter_by(user_id=current_user.id).count()
    }
    
    return render_template('agent/index.html', 
                         recent_sessions=recent_sessions,
                         user_stats=user_stats)

@agent.route('/chat')
@login_required
def chat():
    """Interface de chat"""
    # Criar ou recuperar sessão de chat
    session_id = request.args.get('session_id')
    
    if session_id:
        chat_session = ChatSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id
        ).first_or_404()
    else:
        # Criar nova sessão
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=current_user.id,
            title="Nova Conversa"
        )
        db.session.add(chat_session)
        db.session.commit()
    
    # Buscar histórico de mensagens
    messages = Conversation.query.filter_by(
        session_id=session_id
    ).order_by(Conversation.created_at.asc()).all()
    
    return render_template('agent/chat.html', 
                         chat_session=chat_session,
                         messages=messages)

@agent.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    """API para enviar mensagem ao agente"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        if not session_id:
            return jsonify({'error': 'Session ID obrigatório'}), 400
        
        # Verificar se a sessão pertence ao usuário
        chat_session = ChatSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id
        ).first()
        
        if not chat_session:
            return jsonify({'error': 'Sessão não encontrada'}), 404
        
        # Coletar contexto do usuário
        user_context = _get_user_context()
        
        # Processar mensagem com IA
        start_time = time.time()
        ai_service = AIService()
        ai_response = ai_service.process_message(
            user_message=user_message,
            user_context=user_context,
            conversation_history=_get_conversation_history(session_id)
        )
        response_time = int((time.time() - start_time) * 1000)
        
        # Salvar conversa no banco
        conversation = Conversation(
            user_id=current_user.id,
            session_id=session_id,
            user_message=user_message,
            ai_response=ai_response,
            context_data=user_context,
            response_time_ms=response_time
        )
        
        db.session.add(conversation)
        
        # Atualizar sessão
        chat_session.message_count += 1
        chat_session.last_activity = datetime.utcnow()
        
        # Gerar título automático para a primeira mensagem
        if chat_session.message_count == 1:
            chat_session.title = _generate_session_title(user_message)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'response_time': response_time,
            'conversation_id': conversation.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@agent.route('/api/new_session', methods=['POST'])
@login_required
def new_session():
    """Criar nova sessão de chat"""
    session_id = str(uuid.uuid4())
    
    chat_session = ChatSession(
        id=session_id,
        user_id=current_user.id,
        title="Nova Conversa"
    )
    
    db.session.add(chat_session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'redirect_url': f'/agent/chat?session_id={session_id}'
    })

@agent.route('/api/sessions')
@login_required
def list_sessions():
    """Listar sessões do usuário"""
    sessions = ChatSession.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).order_by(ChatSession.last_activity.desc()).all()
    
    return jsonify([{
        'id': session.id,
        'title': session.title,
        'message_count': session.message_count,
        'last_activity': session.last_activity.isoformat(),
        'created_at': session.created_at.isoformat()
    } for session in sessions])

@agent.route('/api/rate_response', methods=['POST'])
@login_required
def rate_response():
    """Avaliar resposta da IA"""
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    rating = data.get('rating')  # 1-5
    feedback = data.get('feedback', '')
    
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user.id
    ).first_or_404()
    
    conversation.user_rating = rating
    conversation.user_feedback = feedback
    
    db.session.commit()
    
    return jsonify({'success': True})

def _get_user_context():
    """Coletar contexto do usuário para a IA"""
    # Dados das culturas
    cultures = Culture.query.filter_by(user_id=current_user.id).all()
    
    context = {
        'user_id': current_user.id,
        'user_email': current_user.email,
        'total_cultures': len(cultures),
        'cultures': []
    }
    
    for culture in cultures:
        context['cultures'].append({
            'name': culture.name,
            'crop_type': culture.crop_type,
            'area_hectares': culture.area_hectares,
            'status': culture.status,
            'days_since_planting': culture.days_since_planting,
            'location': culture.location
        })
    
    return context

def _get_conversation_history(session_id, limit=10):
    """Buscar histórico recente da conversa"""
    conversations = Conversation.query.filter_by(
        session_id=session_id
    ).order_by(Conversation.created_at.desc()).limit(limit).all()
    
    history = []
    for conv in reversed(conversations):  # Ordem cronológica
        history.append({
            'user': conv.user_message,
            'assistant': conv.ai_response
        })
    
    return history

def _generate_session_title(first_message):
    """Gerar título automático para a sessão"""
    # Títulos baseados em palavras-chave
    keywords = {
        'milho': 'Consulta sobre Milho',
        'trigo': 'Consulta sobre Trigo',
        'batata': 'Consulta sobre Batata',
        'tomate': 'Consulta sobre Tomate',
        'praga': 'Controle de Pragas',
        'doença': 'Doenças das Plantas',
        'fertilizante': 'Fertilização',
        'rega': 'Irrigação',
        'colheita': 'Colheita',
        'plantio': 'Plantio',
        'clima': 'Condições Climáticas'
    }
    
    message_lower = first_message.lower()
    
    for keyword, title in keywords.items():
        if keyword in message_lower:
            return title
    
    # Título genérico baseado no comprimento
    if len(first_message) > 50:
        return first_message[:47] + "..."
    
    return first_message or "Nova Conversa"
```

---

## 🧠 SERVIÇO DE IA

### INTEGRAÇÃO COM OPENAI/CLAUDE

```python
# app/agent/ai_service.py
import openai
import os
from datetime import datetime
import json

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY')
        )
        self.model = "gpt-4"
        
    def process_message(self, user_message, user_context, conversation_history):
        """Processar mensagem do usuário e gerar resposta"""
        
        # Construir prompt do sistema
        system_prompt = self._build_system_prompt(user_context)
        
        # Construir histórico da conversa
        messages = [{"role": "system", "content": system_prompt}]
        
        # Adicionar histórico
        for msg in conversation_history[-5:]:  # Últimas 5 mensagens
            messages.append({"role": "user", "content": msg["user"]})
            messages.append({"role": "assistant", "content": msg["assistant"]})
        
        # Adicionar mensagem atual
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente em alguns momentos. (Erro: {str(e)})"
    
    def _build_system_prompt(self, user_context):
        """Construir prompt do sistema com contexto do usuário"""
        
        base_prompt = """Você é o Agente Agrícola, um assistente de IA especializado em agricultura familiar portuguesa. 

CARACTERÍSTICAS:
- Especialista em agricultura familiar em Portugal
- Conhece a legislação agrícola portuguesa e europeia
- Fala português de Portugal (não brasileiro)
- É amigável, prestativo e prático
- Oferece conselhos baseados em evidências científicas
- Considera as condições climáticas de Portugal

INSTRUÇÕES:
1. Responda sempre em português de Portugal
2. Seja específico para a agricultura familiar (pequenas propriedades)
3. Considere as condições climáticas e solo de Portugal
4. Mencione legislação relevante quando apropriado
5. Seja prático e ofereça soluções viáveis
6. Use linguagem acessível, evite jargão excessivo
7. Quando não souber algo, admita e sugira onde buscar informação

CONTEXTO DO UTILIZADOR:
"""
        
        # Adicionar contexto específico do usuário
        if user_context.get('cultures'):
            base_prompt += f"\nO utilizador tem {user_context['total_cultures']} cultura(s) registada(s):\n"
            
            for culture in user_context['cultures']:
                base_prompt += f"- {culture['name']}: {culture['crop_type']}, {culture['area_hectares']} hectares"
                if culture['location']:
                    base_prompt += f", localizada em {culture['location']}"
                base_prompt += f" (plantada há {culture['days_since_planting']} dias)\n"
        else:
            base_prompt += "\nO utilizador ainda não registou nenhuma cultura no sistema.\n"
        
        base_prompt += f"""
TÓPICOS QUE PODE ABORDAR:
- Cultivo de cereais, hortícolas, frutícolas
- Controle de pragas e doenças
- Fertilização e nutrição das plantas
- Irrigação e gestão da água
- Rotação de culturas
- Agricultura biológica
- Subsídios e apoios da PAC (Política Agrícola Comum)
- Comercialização de produtos agrícolas
- Sustentabilidade e práticas ambientais
- Tecnologia agrícola adequada para pequenas explorações

RESPONDA DE FORMA:
- Clara e objetiva
- Adaptada ao contexto português
- Com sugestões práticas
- Considerando o orçamento limitado da agricultura familiar
- Incluindo quando possível referências a recursos locais

Data atual: {datetime.now().strftime('%d/%m/%Y')}
"""
        
        return base_prompt
    
    def generate_suggestions(self, user_context):
        """Gerar sugestões de perguntas baseadas no contexto"""
        
        suggestions = [
            "Como posso melhorar a produtividade das minhas culturas?",
            "Que subsídios estão disponíveis para agricultura familiar?",
            "Como controlar pragas de forma natural?",
            "Qual é a melhor época para plantar em Portugal?",
            "Como fazer rotação de culturas?"
        ]
        
        # Sugestões específicas baseadas nas culturas do usuário
        if user_context.get('cultures'):
            for culture in user_context['cultures']:
                crop_type = culture['crop_type']
                
                if crop_type == 'cereais':
                    suggestions.append(f"Como otimizar a produção de {culture['name']}?")
                elif crop_type == 'hortícolas':
                    suggestions.append(f"Que cuidados devo ter com {culture['name']}?")
                elif crop_type == 'frutícolas':
                    suggestions.append(f"Quando é a melhor época para podar {culture['name']}?")
        
        return suggestions[:6]  # Máximo 6 sugestões
```

---

## 🎨 TEMPLATES HTML

### TEMPLATE PRINCIPAL - INTERFACE DO AGENTE

```html
<!-- templates/agent/index.html -->
{% extends "base.html" %}

{% block title %}Agente IA - AgTech Portugal{% endblock %}

{% block extra_css %}
<style>
.agent-hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px;
    padding: 2rem;
    margin-bottom: 2rem;
}

.chat-preview {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
}

.suggestion-card {
    background: white;
    border: 1px solid #e9ecef;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.3s;
}

.suggestion-card:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    border: 1px solid #e9ecef;
}

.ai-avatar {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    margin: 0 auto 1rem;
}
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Hero Section -->
    <div class="agent-hero">
        <div class="row align-items-center">
            <div class="col-md-8">
                <h1><i class="fas fa-robot"></i> Agente Agrícola IA</h1>
                <p class="lead mb-3">
                    O seu assistente pessoal especializado em agricultura familiar portuguesa. 
                    Tire dúvidas, receba conselhos personalizados e otimize a sua produção.
                </p>
                <a href="{{ url_for('agent.chat') }}" class="btn btn-light btn-lg">
                    <i class="fas fa-comments"></i> Iniciar Conversa
                </a>
            </div>
            <div class="col-md-4 text-center">
                <div class="ai-avatar" style="width: 120px; height: 120px; font-size: 48px;">
                    🤖
                </div>
            </div>
        </div>
    </div>
    
    <!-- Estatísticas do Usuário -->
    <div class="stats-grid">
        <div class="stat-card">
            <h3 class="text-primary">{{ user_stats.total_cultures }}</h3>
            <p class="mb-0">Culturas Registadas</p>
        </div>
        <div class="stat-card">
            <h3 class="text-success">{{ user_stats.active_cultures }}</h3>
            <p class="mb-0">Culturas Ativas</p>
        </div>
        <div class="stat-card">
            <h3 class="text-info">{{ user_stats.total_conversations }}</h3>
            <p class="mb-0">Conversas Realizadas</p>
        </div>
        <div class="stat-card">
            <h3 class="text-warning">24/7</h3>
            <p class="mb-0">Disponibilidade</p>
        </div>
    </div>
    
    <div class="row">
        <!-- Conversas Recentes -->
        <div class="col-md-6">
            <h3><i class="fas fa-history"></i> Conversas Recentes</h3>
            
            {% if recent_sessions %}
                {% for session in recent_sessions %}
                <div class="chat-preview">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">{{ session.title }}</h6>
                            <small class="text-muted">
                                {{ session.message_count }} mensagem{% if session.message_count != 1 %}s{% endif %}
                                • {{ session.last_activity.strftime('%d/%m/%Y às %H:%M') }}
                            </small>
                        </div>
                        <a href="{{ url_for('agent.chat', session_id=session.id) }}" 
                           class="btn btn-sm btn-outline-primary">
                            Continuar
                        </a>
                    </div>
                </div>
                {% endfor %}
                
                <div class="text-center mt-3">
                    <button class="btn btn-outline-secondary" onclick="loadAllSessions()">
                        Ver Todas as Conversas
                    </button>
                </div>
            {% else %}
                <div class="text-center py-4">
                    <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Ainda não teve conversas com o agente.</p>
                    <a href="{{ url_for('agent.chat') }}" class="btn btn-primary">
                        Iniciar Primeira Conversa
                    </a>
                </div>
            {% endif %}
        </div>
        
        <!-- Sugestões de Perguntas -->
        <div class="col-md-6">
            <h3><i class="fas fa-lightbulb"></i> Sugestões de Perguntas</h3>
            
            <div class="suggestion-card" onclick="startChatWithMessage('Como posso melhorar a produtividade das minhas culturas?')">
                <h6><i class="fas fa-chart-line text-success"></i> Produtividade</h6>
                <p class="mb-0">Como posso melhorar a produtividade das minhas culturas?</p>
            </div>
            
            <div class="suggestion-card" onclick="startChatWithMessage('Que subsídios estão disponíveis para agricultura familiar?')">
                <h6><i class="fas fa-euro-sign text-primary"></i> Subsídios</h6>
                <p class="mb-0">Que subsídios estão disponíveis para agricultura familiar?</p>
            </div>
            
            <div class="suggestion-card" onclick="startChatWithMessage('Como controlar pragas de forma natural?')">
                <h6><i class="fas fa-bug text-warning"></i> Controle de Pragas</h6>
                <p class="mb-0">Como controlar pragas de forma natural?</p>
            </div>
            
            <div class="suggestion-card" onclick="startChatWithMessage('Qual é a melhor época para plantar em Portugal?')">
                <h6><i class="fas fa-calendar text-info"></i> Época de Plantio</h6>
                <p class="mb-0">Qual é a melhor época para plantar em Portugal?</p>
            </div>
            
            {% if user_stats.total_cultures > 0 %}
            <div class="suggestion-card" onclick="startChatWithMessage('Analise as minhas culturas e dê sugestões de melhoria')">
                <h6><i class="fas fa-seedling text-success"></i> Análise Personalizada</h6>
                <p class="mb-0">Analise as minhas culturas e dê sugestões de melhoria</p>
            </div>
            {% endif %}
            
            <div class="suggestion-card" onclick="startChatWithMessage('Como fazer rotação de culturas?')">
                <h6><i class="fas fa-sync text-secondary"></i> Rotação de Culturas</h6>
                <p class="mb-0">Como fazer rotação de culturas?</p>
            </div>
        </div>
    </div>
    
    <!-- Recursos Adicionais -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-info-circle"></i> O que o Agente Agrícola pode fazer por si</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6><i class="fas fa-leaf text-success"></i> Conselhos Especializados</h6>
                            <p>Orientações específicas para agricultura familiar portuguesa, considerando clima, solo e legislação local.</p>
                        </div>
                        <div class="col-md-4">
                            <h6><i class="fas fa-chart-bar text-primary"></i> Análise Personalizada</h6>
                            <p>Avaliação das suas culturas registadas com sugestões de melhoria e otimização.</p>
                        </div>
                        <div class="col-md-4">
                            <h6><i class="fas fa-clock text-info"></i> Disponível 24/7</h6>
                            <p>Assistência disponível a qualquer hora, com respostas rápidas e precisas.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
function startChatWithMessage(message) {
    // Criar nova sessão e iniciar com mensagem específica
    fetch('/agent/api/new_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirecionar para chat com mensagem pré-definida
            const url = `/agent/chat?session_id=${data.session_id}&message=${encodeURIComponent(message)}`;
            window.location.href = url;
        }
    })
    .catch(error => {
        console.error('Erro ao criar sessão:', error);
        // Fallback: ir para chat normal
        window.location.href = '/agent/chat';
    });
}

function loadAllSessions() {
    fetch('/agent/api/sessions')
        .then(response => response.json())
        .then(sessions => {
            // Implementar modal ou página com todas as sessões
            console.log('Todas as sessões:', sessions);
            // Por enquanto, redirecionar para chat
            window.location.href = '/agent/chat';
        })
        .catch(error => console.error('Erro ao carregar sessões:', error));
}
</script>
{% endblock %}
```

### TEMPLATE DE CHAT

```html
<!-- templates/agent/chat.html -->
{% extends "base.html" %}

{% block title %}Chat - Agente IA - AgTech Portugal{% endblock %}

{% block extra_css %}
<style>
.chat-container {
    height: calc(100vh - 200px);
    display: flex;
    flex-direction: column;
}

.chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px 10px 0 0;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background: #f8f9fa;
    max-height: 500px;
}

.message {
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
}

.message.user {
    justify-content: flex-end;
}

.message.assistant {
    justify-content: flex-start;
}

.message-content {
    max-width: 70%;
    padding: 0.75rem 1rem;
    border-radius: 18px;
    position: relative;
}

.message.user .message-content {
    background: #667eea;
    color: white;
    border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
    background: white;
    color: #333;
    border: 1px solid #e9ecef;
    border-bottom-left-radius: 4px;
}

.message-time {
    font-size: 0.75rem;
    opacity: 0.7;
    margin-top: 0.25rem;
}

.chat-input {
    background: white;
    border-top: 1px solid #e9ecef;
    padding: 1rem;
    border-radius: 0 0 10px 10px;
}

.typing-indicator {
    display: none;
    padding: 0.5rem 1rem;
    background: white;
    border-radius: 18px;
    border: 1px solid #e9ecef;
    max-width: 100px;
}

.typing-dots {
    display: flex;
    align-items: center;
    gap: 4px;
}

.typing-dots span {
    height: 8px;
    width: 8px;
    background: #999;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    margin: 0 0.5rem;
    flex-shrink: 0;
}

.avatar.user {
    background: #28a745;
    color: white;
}

.avatar.assistant {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.quick-suggestions {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.quick-suggestion {
    background: #e9ecef;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.3s;
}

.quick-suggestion:hover {
    background: #667eea;
    color: white;
}

@media (max-width: 768px) {
    .message-content {
        max-width: 85%;
    }
    
    .chat-container {
        height: calc(100vh - 150px);
    }
}
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card chat-container">
                <!-- Cabeçalho do Chat -->
                <div class="chat-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="mb-0">{{ chat_session.title }}</h5>
                            <small>Agente Agrícola IA • Online</small>
                        </div>
                        <div>
                            <button class="btn btn-light btn-sm" onclick="newSession()">
                                <i class="fas fa-plus"></i> Nova Conversa
                            </button>
                            <a href="{{ url_for('agent.index') }}" class="btn btn-light btn-sm">
                                <i class="fas fa-arrow-left"></i> Voltar
                            </a>
                        </div>
                    </div>
                </div>
                
                <!-- Mensagens -->
                <div class="chat-messages" id="chatMessages">
                    {% if not messages %}
                    <!-- Mensagem de boas-vindas -->
                    <div class="message assistant">
                        <div class="avatar assistant">🤖</div>
                        <div class="message-content">
                            <p class="mb-0">
                                Olá! Sou o seu Agente Agrícola IA, especializado em agricultura familiar portuguesa. 
                                Como posso ajudá-lo hoje?
                            </p>
                            <div class="message-time">Agora</div>
                        </div>
                    </div>
                    {% else %}
                        {% for message in messages %}
                        <div class="message user">
                            <div class="message-content">
                                <p class="mb-0">{{ message.user_message }}</p>
                                <div class="message-time">{{ message.created_at.strftime('%H:%M') }}</div>
                            </div>
                            <div class="avatar user">{{ current_user.email[0].upper() }}</div>
                        </div>
                        
                        <div class="message assistant">
                            <div class="avatar assistant">🤖</div>
                            <div class="message-content">
                                <div class="message-text">{{ message.ai_response|safe }}</div>
                                <div class="message-time">{{ message.created_at.strftime('%H:%M') }}</div>
                                
                                <!-- Botões de avaliação -->
                                <div class="mt-2">
                                    <button class="btn btn-sm btn-outline-success" onclick="rateResponse({{ message.id }}, 5)">
                                        <i class="fas fa-thumbs-up"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="rateResponse({{ message.id }}, 1)">
                                        <i class="fas fa-thumbs-down"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% endif %}
                    
                    <!-- Indicador de digitação -->
                    <div class="message assistant typing-indicator" id="typingIndicator">
                        <div class="avatar assistant">🤖</div>
                        <div class="typing-indicator">
                            <div class="typing-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Input de Mensagem -->
                <div class="chat-input">
                    <!-- Sugestões rápidas -->
                    <div class="quick-suggestions" id="quickSuggestions">
                        <button class="quick-suggestion" onclick="sendQuickMessage('Como está o tempo para as minhas culturas?')">
                            Clima hoje
                        </button>
                        <button class="quick-suggestion" onclick="sendQuickMessage('Que tarefas devo fazer esta semana?')">
                            Tarefas da semana
                        </button>
                        <button class="quick-suggestion" onclick="sendQuickMessage('Analise as minhas culturas')">
                            Analisar culturas
                        </button>
                    </div>
                    
                    <form id="chatForm" onsubmit="sendMessage(event)">
                        <div class="input-group">
                            <input type="text" 
                                   class="form-control" 
                                   id="messageInput" 
                                   placeholder="Digite sua mensagem..."
                                   autocomplete="off"
                                   maxlength="1000">
                            <button type="submit" class="btn btn-primary" id="sendButton">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
const sessionId = '{{ chat_session.id }}';
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');

// Verificar se há mensagem pré-definida na URL
const urlParams = new URLSearchParams(window.location.search);
const preMessage = urlParams.get('message');
if (preMessage) {
    messageInput.value = preMessage;
    sendMessage(null, preMessage);
}

function sendMessage(event, predefinedMessage = null) {
    if (event) event.preventDefault();
    
    const message = predefinedMessage || messageInput.value.trim();
    if (!message) return;
    
    // Adicionar mensagem do usuário à interface
    addUserMessage(message);
    
    // Limpar input e desabilitar
    messageInput.value = '';
    messageInput.disabled = true;
    sendButton.disabled = true;
    
    // Mostrar indicador de digitação
    showTypingIndicator();
    
    // Enviar para API
    fetch('/agent/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            session_id: sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        
        if (data.success) {
            addAssistantMessage(data.response, data.conversation_id);
            hideQuickSuggestions();
        } else {
            addAssistantMessage('Desculpe, ocorreu um erro. Tente novamente.', null);
        }
    })
    .catch(error => {
        hideTypingIndicator();
        addAssistantMessage('Erro de conexão. Verifique sua internet e tente novamente.', null);
        console.error('Erro:', error);
    })
    .finally(() => {
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    });
}

function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p class="mb-0">${escapeHtml(message)}</p>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
        <div class="avatar user">${'{{ current_user.email[0].upper() }}'}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addAssistantMessage(message, conversationId) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const ratingButtons = conversationId ? `
        <div class="mt-2">
            <button class="btn btn-sm btn-outline-success" onclick="rateResponse(${conversationId}, 5)">
                <i class="fas fa-thumbs-up"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="rateResponse(${conversationId}, 1)">
                <i class="fas fa-thumbs-down"></i>
            </button>
        </div>
    ` : '';
    
    messageDiv.innerHTML = `
        <div class="avatar assistant">🤖</div>
        <div class="message-content">
            <div class="message-text">${formatMessage(message)}</div>
            <div class="message-time">${getCurrentTime()}</div>
            ${ratingButtons}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

function hideQuickSuggestions() {
    document.getElementById('quickSuggestions').style.display = 'none';
}

function sendQuickMessage(message) {
    sendMessage(null, message);
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getCurrentTime() {
    return new Date().toLocaleTimeString('pt-PT', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMessage(message) {
    // Converter quebras de linha em <br>
    return message.replace(/\n/g, '<br>');
}

function rateResponse(conversationId, rating) {
    fetch('/agent/api/rate_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            conversation_id: conversationId,
            rating: rating
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Feedback visual
            const button = event.target.closest('button');
            button.classList.add(rating > 3 ? 'btn-success' : 'btn-danger');
            button.classList.remove('btn-outline-success', 'btn-outline-danger');
        }
    })
    .catch(error => console.error('Erro ao avaliar:', error));
}

function newSession() {
    fetch('/agent/api/new_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        }
    })
    .catch(error => console.error('Erro ao criar sessão:', error));
}

// Auto-focus no input
messageInput.focus();

// Scroll inicial para o final
scrollToBottom();

// Enter para enviar (Shift+Enter para nova linha)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
</script>
{% endblock %}
```

---

## ✅ CRITÉRIOS DE VALIDAÇÃO

### TESTES OBRIGATÓRIOS

**1. Funcionalidade Básica:**
- [ ] Rota `/agent` carrega sem redirecionamento
- [ ] Interface de chat funcional
- [ ] Mensagens são enviadas e recebidas
- [ ] Histórico de conversas é mantido
- [ ] Sessões são criadas e gerenciadas

**2. Inteligência Artificial:**
- [ ] Respostas contextuais sobre agricultura
- [ ] Integração com dados das culturas do usuário
- [ ] Respostas em português de Portugal
- [ ] Conhecimento específico sobre agricultura familiar

**3. Interface e UX:**
- [ ] Design responsivo (mobile/desktop)
- [ ] Indicadores de digitação
- [ ] Sugestões de perguntas
- [ ] Sistema de avaliação de respostas

**4. Performance:**
- [ ] Respostas em <5 segundos
- [ ] Interface fluida sem travamentos
- [ ] Histórico carrega rapidamente

### SCRIPT DE TESTE

```python
# test_agent.py
import requests
import json

def test_agent_functionality():
    base_url = "http://localhost:5000"
    
    # Login
    session = requests.Session()
    login_data = {
        'email': 'teste.final.sprint1@agrotech.pt',
        'password': 'TesteFinalSprint2025!'
    }
    session.post(f"{base_url}/auth/login", data=login_data)
    
    # Teste 1: Acessar página do agente
    response = session.get(f"{base_url}/agent")
    assert response.status_code == 200, "Página do agente inacessível"
    
    # Teste 2: Criar nova sessão
    response = session.post(f"{base_url}/agent/api/new_session")
    data = response.json()
    assert data['success'], "Falha ao criar sessão"
    session_id = data['session_id']
    
    # Teste 3: Enviar mensagem
    message_data = {
        'message': 'Como plantar milho em Portugal?',
        'session_id': session_id
    }
    response = session.post(f"{base_url}/agent/api/send_message", json=message_data)
    data = response.json()
    assert data['success'], "Falha ao enviar mensagem"
    assert len(data['response']) > 10, "Resposta muito curta"
    
    print("✅ Todos os testes do agente IA passaram!")

if __name__ == "__main__":
    test_agent_functionality()
```

---

## 📦 ENTREGÁVEIS OBRIGATÓRIOS

### 1. CÓDIGO BACKEND
- [ ] `app/models/conversation.py` - Modelos de conversa
- [ ] `app/agent/routes.py` - Controller do agente
- [ ] `app/agent/ai_service.py` - Serviço de IA
- [ ] Migration para tabelas de conversa

### 2. TEMPLATES FRONTEND
- [ ] `templates/agent/index.html` - Interface principal
- [ ] `templates/agent/chat.html` - Interface de chat
- [ ] CSS customizado para chat
- [ ] JavaScript para interações

### 3. INTEGRAÇÃO
- [ ] Blueprint registrado em `app/__init__.py`
- [ ] Configuração da API OpenAI/Claude
- [ ] Menu de navegação atualizado
- [ ] Integração com dados das culturas

### 4. TESTES E DOCUMENTAÇÃO
- [ ] Testes unitários do serviço de IA
- [ ] Script de validação
- [ ] Documentação da API
- [ ] Guia de uso para agricultores

---

## 🚀 RESULTADO ESPERADO

### ANTES DA IMPLEMENTAÇÃO
- Funcionalidade Agente IA: 0%
- Rota /agent: Inacessível
- Sem diferencial competitivo

### APÓS A IMPLEMENTAÇÃO
- Funcionalidade Agente IA: 100%
- Chat conversacional funcionando
- Score Sprint 3: +25% (de 75% para 100%)

### VALIDAÇÃO FINAL
```bash
# Teste manual
1. Acessar https://www.agenteagricola.com/agent
2. Iniciar conversa
3. Fazer pergunta sobre agricultura
4. Verificar resposta contextual

# Teste automatizado
python3 validacao_automatizada_sprint3.py
# Resultado esperado: ai_agent_functionality: 100%
```

---

**🤖 Esta implementação transformará o AgroTech Portugal no primeiro assistente de IA especializado em agricultura familiar portuguesa, oferecendo um diferencial competitivo único no mercado!**

