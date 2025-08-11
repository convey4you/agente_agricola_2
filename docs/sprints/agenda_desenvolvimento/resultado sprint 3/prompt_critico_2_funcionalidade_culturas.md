# 🌱 PROMPT CRÍTICO 2: IMPLEMENTAÇÃO DA FUNCIONALIDADE CULTURAS

**DEPENDÊNCIA:** PROMPT 1 (Autenticação corrigida)  
**PRIORIDADE:** ALTA - 48-72 HORAS  
**OBJETIVO:** Funcionalidade completa de gestão de culturas  
**IMPACTO:** 25% do score total do Sprint 3

---

## 🎯 CONTEXTO EXECUTIVO

Você é um desenvolvedor especialista em Flask trabalhando na **funcionalidade principal** do AgroTech Portugal: **Gestão de Culturas**. Esta é a funcionalidade core que permite aos agricultores familiares portugueses gerenciar suas plantações de forma inteligente.

**IMPORTANTE:** Este prompt só deve ser executado **APÓS** a correção do sistema de autenticação (Prompt 1), garantindo que a rota `/cultures` seja acessível sem redirecionamento.

### 📊 CONTEXTO DO PROBLEMA

**Situação Atual:**
- ❌ Funcionalidade Culturas: 0% implementada
- ❌ Rota `/cultures` inacessível (redirecionamento para login)
- ❌ Nenhum CRUD de culturas disponível
- ❌ Dashboard não mostra dados reais de culturas

**Objetivo Final:**
- ✅ CRUD completo de culturas
- ✅ Interface intuitiva para agricultores
- ✅ Integração com dashboard principal
- ✅ Dados reais substituindo placeholders

---

## 🛠️ ESPECIFICAÇÕES TÉCNICAS

### Ambiente de Desenvolvimento
- **Framework:** Flask 3.1.1 + SQLAlchemy 2.0.41
- **Banco de Dados:** PostgreSQL (Railway)
- **Frontend:** HTML5 + CSS3 + JavaScript (Bootstrap 5)
- **Deploy:** Railway (automático via GitHub)
- **Repositório:** https://github.com/convey4you/agente_agricola

### Ferramentas Obrigatórias
- **VS Code** com GitHub Copilot
- **Flask-Migrate** para migrations
- **WTForms** para formulários
- **Pillow** para upload de imagens (opcional)

---

## 📋 ESPECIFICAÇÕES FUNCIONAIS

### FUNCIONALIDADES OBRIGATÓRIAS

#### 1. GESTÃO BÁSICA DE CULTURAS
- [x] **Listar Culturas** - Visualizar todas as culturas do usuário
- [x] **Cadastrar Cultura** - Adicionar nova cultura
- [x] **Editar Cultura** - Modificar dados existentes
- [x] **Excluir Cultura** - Remover cultura com confirmação
- [x] **Visualizar Detalhes** - Página individual da cultura

#### 2. INFORMAÇÕES DA CULTURA
- [x] **Dados Básicos:** Nome, tipo de cultura, área (hectares)
- [x] **Datas:** Plantio, previsão de colheita
- [x] **Status:** Ativa, colhida, perdida
- [x] **Localização:** Região/distrito em Portugal
- [x] **Observações:** Notas do agricultor

#### 3. INTEGRAÇÃO COM SISTEMA
- [x] **Dashboard Atualizado** - Contadores e métricas reais
- [x] **Filtros e Busca** - Encontrar culturas específicas
- [x] **Paginação** - Para muitas culturas
- [x] **Validações** - Dados consistentes e seguros

---

## 🗃️ MODELO DE DADOS

### TABELA CULTURES

```python
# app/models/culture.py
from datetime import datetime, date
from app import db

class Culture(db.Model):
    __tablename__ = 'cultures'
    
    # Chaves
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Dados básicos
    name = db.Column(db.String(100), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)  # milho, trigo, batata, etc.
    variety = db.Column(db.String(100))  # variedade específica
    
    # Área e localização
    area_hectares = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100))  # distrito/região
    field_name = db.Column(db.String(50))  # nome do campo/parcela
    
    # Datas importantes
    planting_date = db.Column(db.Date, nullable=False)
    expected_harvest_date = db.Column(db.Date)
    actual_harvest_date = db.Column(db.Date)
    
    # Status e controle
    status = db.Column(db.String(20), default='active')  # active, harvested, lost
    growth_stage = db.Column(db.String(30))  # germinação, crescimento, floração, etc.
    
    # Informações adicionais
    notes = db.Column(db.Text)
    estimated_yield = db.Column(db.Float)  # produção estimada (toneladas)
    actual_yield = db.Column(db.Float)  # produção real
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('cultures', lazy=True))
    
    def __repr__(self):
        return f'<Culture {self.name} - {self.crop_type}>'
    
    @property
    def days_since_planting(self):
        """Calcula dias desde o plantio"""
        if self.planting_date:
            return (date.today() - self.planting_date).days
        return 0
    
    @property
    def days_to_harvest(self):
        """Calcula dias até a colheita prevista"""
        if self.expected_harvest_date:
            return (self.expected_harvest_date - date.today()).days
        return None
    
    @property
    def status_display(self):
        """Status em português"""
        status_map = {
            'active': 'Ativa',
            'harvested': 'Colhida',
            'lost': 'Perdida'
        }
        return status_map.get(self.status, 'Desconhecido')
    
    def to_dict(self):
        """Converte para dicionário (útil para APIs)"""
        return {
            'id': self.id,
            'name': self.name,
            'crop_type': self.crop_type,
            'area_hectares': self.area_hectares,
            'status': self.status,
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'days_since_planting': self.days_since_planting,
            'days_to_harvest': self.days_to_harvest
        }
```

### MIGRATION NECESSÁRIA

```python
# migrations/versions/xxx_add_cultures_table.py
"""Adicionar tabela cultures

Revision ID: xxx
Revises: yyy
Create Date: 2025-08-01
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('cultures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('crop_type', sa.String(length=50), nullable=False),
        sa.Column('variety', sa.String(length=100), nullable=True),
        sa.Column('area_hectares', sa.Float(), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('field_name', sa.String(length=50), nullable=True),
        sa.Column('planting_date', sa.Date(), nullable=False),
        sa.Column('expected_harvest_date', sa.Date(), nullable=True),
        sa.Column('actual_harvest_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('growth_stage', sa.String(length=30), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('estimated_yield', sa.Float(), nullable=True),
        sa.Column('actual_yield', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('cultures')
```

---

## 🎮 CONTROLLER E ROTAS

### CONTROLLER PRINCIPAL

```python
# app/cultures/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.culture import Culture
from app.cultures.forms import CultureForm
from datetime import datetime, date

cultures = Blueprint('cultures', __name__, url_prefix='/cultures')

@cultures.route('/')
@login_required
def index():
    """Lista todas as culturas do usuário"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = Culture.query.filter_by(user_id=current_user.id)
    
    # Aplicar filtros
    if search:
        query = query.filter(Culture.name.contains(search) | 
                           Culture.crop_type.contains(search))
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(Culture.created_at.desc())
    
    # Paginação
    cultures_paginated = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Estatísticas para o cabeçalho
    stats = {
        'total': Culture.query.filter_by(user_id=current_user.id).count(),
        'active': Culture.query.filter_by(user_id=current_user.id, status='active').count(),
        'harvested': Culture.query.filter_by(user_id=current_user.id, status='harvested').count(),
        'total_area': db.session.query(db.func.sum(Culture.area_hectares)).filter_by(user_id=current_user.id).scalar() or 0
    }
    
    return render_template('cultures/index.html', 
                         cultures=cultures_paginated,
                         stats=stats,
                         search=search,
                         status_filter=status_filter)

@cultures.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Cadastrar nova cultura"""
    form = CultureForm()
    
    if form.validate_on_submit():
        culture = Culture(
            user_id=current_user.id,
            name=form.name.data,
            crop_type=form.crop_type.data,
            variety=form.variety.data,
            area_hectares=form.area_hectares.data,
            location=form.location.data,
            field_name=form.field_name.data,
            planting_date=form.planting_date.data,
            expected_harvest_date=form.expected_harvest_date.data,
            status=form.status.data,
            growth_stage=form.growth_stage.data,
            notes=form.notes.data,
            estimated_yield=form.estimated_yield.data
        )
        
        db.session.add(culture)
        db.session.commit()
        
        flash(f'Cultura "{culture.name}" cadastrada com sucesso!', 'success')
        return redirect(url_for('cultures.index'))
    
    return render_template('cultures/form.html', form=form, title='Nova Cultura')

@cultures.route('/<int:id>')
@login_required
def detail(id):
    """Visualizar detalhes da cultura"""
    culture = Culture.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    return render_template('cultures/detail.html', culture=culture)

@cultures.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar cultura existente"""
    culture = Culture.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CultureForm(obj=culture)
    
    if form.validate_on_submit():
        form.populate_obj(culture)
        culture.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Cultura "{culture.name}" atualizada com sucesso!', 'success')
        return redirect(url_for('cultures.detail', id=culture.id))
    
    return render_template('cultures/form.html', form=form, culture=culture, title='Editar Cultura')

@cultures.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Excluir cultura"""
    culture = Culture.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    culture_name = culture.name
    db.session.delete(culture)
    db.session.commit()
    
    flash(f'Cultura "{culture_name}" removida com sucesso!', 'success')
    return redirect(url_for('cultures.index'))

# API Endpoints para AJAX
@cultures.route('/api/stats')
@login_required
def api_stats():
    """Retorna estatísticas das culturas para o dashboard"""
    stats = {
        'total_cultures': Culture.query.filter_by(user_id=current_user.id).count(),
        'active_cultures': Culture.query.filter_by(user_id=current_user.id, status='active').count(),
        'total_area': float(db.session.query(db.func.sum(Culture.area_hectares)).filter_by(user_id=current_user.id).scalar() or 0),
        'recent_plantings': Culture.query.filter_by(user_id=current_user.id).filter(
            Culture.planting_date >= date.today().replace(day=1)
        ).count()
    }
    
    return jsonify(stats)

@cultures.route('/api/list')
@login_required
def api_list():
    """API para listar culturas (útil para outros módulos)"""
    cultures_list = Culture.query.filter_by(user_id=current_user.id).all()
    return jsonify([culture.to_dict() for culture in cultures_list])
```

---

## 📝 FORMULÁRIOS (WTForms)

### FORMULÁRIO PRINCIPAL

```python
# app/cultures/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import date

class CultureForm(FlaskForm):
    # Dados básicos
    name = StringField('Nome da Cultura', 
                      validators=[DataRequired(), Length(min=2, max=100)],
                      render_kw={'placeholder': 'Ex: Milho do Campo Norte'})
    
    crop_type = SelectField('Tipo de Cultura',
                           validators=[DataRequired()],
                           choices=[
                               ('', 'Selecione o tipo'),
                               ('cereais', 'Cereais'),
                               ('leguminosas', 'Leguminosas'),
                               ('hortícolas', 'Hortícolas'),
                               ('frutícolas', 'Frutícolas'),
                               ('forragens', 'Forragens'),
                               ('oleaginosas', 'Oleaginosas'),
                               ('outros', 'Outros')
                           ])
    
    variety = StringField('Variedade',
                         validators=[Optional(), Length(max=100)],
                         render_kw={'placeholder': 'Ex: Milho Doce Golden Bantam'})
    
    # Área e localização
    area_hectares = FloatField('Área (hectares)',
                              validators=[DataRequired(), NumberRange(min=0.01, max=10000)],
                              render_kw={'placeholder': '0.5', 'step': '0.01'})
    
    location = StringField('Localização',
                          validators=[Optional(), Length(max=100)],
                          render_kw={'placeholder': 'Ex: Braga, Minho'})
    
    field_name = StringField('Nome do Campo/Parcela',
                            validators=[Optional(), Length(max=50)],
                            render_kw={'placeholder': 'Ex: Campo Norte'})
    
    # Datas
    planting_date = DateField('Data de Plantio',
                             validators=[DataRequired()],
                             default=date.today)
    
    expected_harvest_date = DateField('Previsão de Colheita',
                                     validators=[Optional()])
    
    # Status
    status = SelectField('Status',
                        validators=[DataRequired()],
                        choices=[
                            ('active', 'Ativa'),
                            ('harvested', 'Colhida'),
                            ('lost', 'Perdida')
                        ],
                        default='active')
    
    growth_stage = SelectField('Estágio de Crescimento',
                              validators=[Optional()],
                              choices=[
                                  ('', 'Selecione o estágio'),
                                  ('germinacao', 'Germinação'),
                                  ('crescimento', 'Crescimento'),
                                  ('floracao', 'Floração'),
                                  ('frutificacao', 'Frutificação'),
                                  ('maturacao', 'Maturação'),
                                  ('colheita', 'Pronto para Colheita')
                              ])
    
    # Informações adicionais
    estimated_yield = FloatField('Produção Estimada (toneladas)',
                                validators=[Optional(), NumberRange(min=0)],
                                render_kw={'placeholder': '2.5', 'step': '0.1'})
    
    notes = TextAreaField('Observações',
                         validators=[Optional(), Length(max=1000)],
                         render_kw={'rows': 4, 'placeholder': 'Notas sobre a cultura, tratamentos aplicados, etc.'})
    
    def validate_expected_harvest_date(self, field):
        """Validação customizada para data de colheita"""
        if field.data and self.planting_date.data:
            if field.data <= self.planting_date.data:
                raise ValidationError('A data de colheita deve ser posterior à data de plantio.')
```

---

## 🎨 TEMPLATES HTML

### TEMPLATE PRINCIPAL - LISTAGEM

```html
<!-- templates/cultures/index.html -->
{% extends "base.html" %}

{% block title %}Culturas - AgTech Portugal{% endblock %}

{% block extra_css %}
<style>
.culture-card {
    transition: transform 0.2s;
    border-left: 4px solid #28a745;
}

.culture-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.status-badge {
    font-size: 0.8em;
    padding: 0.3em 0.6em;
}

.stats-card {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    border-radius: 10px;
}
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Cabeçalho com estatísticas -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h1><i class="fas fa-seedling text-success"></i> Gestão de Culturas</h1>
                <a href="{{ url_for('cultures.new') }}" class="btn btn-success">
                    <i class="fas fa-plus"></i> Nova Cultura
                </a>
            </div>
        </div>
    </div>
    
    <!-- Estatísticas -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body text-center">
                    <h3 class="mb-0">{{ stats.total }}</h3>
                    <small>Culturas Totais</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body text-center">
                    <h3 class="mb-0">{{ stats.active }}</h3>
                    <small>Culturas Ativas</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body text-center">
                    <h3 class="mb-0">{{ "%.1f"|format(stats.total_area) }}</h3>
                    <small>Hectares Totais</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body text-center">
                    <h3 class="mb-0">{{ stats.harvested }}</h3>
                    <small>Colhidas</small>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Filtros e busca -->
    <div class="row mb-3">
        <div class="col-md-8">
            <form method="GET" class="d-flex">
                <input type="text" name="search" class="form-control me-2" 
                       placeholder="Buscar por nome ou tipo..." value="{{ search }}">
                <select name="status" class="form-select me-2" style="width: auto;">
                    <option value="">Todos os status</option>
                    <option value="active" {% if status_filter == 'active' %}selected{% endif %}>Ativas</option>
                    <option value="harvested" {% if status_filter == 'harvested' %}selected{% endif %}>Colhidas</option>
                    <option value="lost" {% if status_filter == 'lost' %}selected{% endif %}>Perdidas</option>
                </select>
                <button type="submit" class="btn btn-outline-primary">
                    <i class="fas fa-search"></i>
                </button>
            </form>
        </div>
    </div>
    
    <!-- Lista de culturas -->
    {% if cultures.items %}
        <div class="row">
            {% for culture in cultures.items %}
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card culture-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">{{ culture.name }}</h5>
                            <span class="badge status-badge 
                                {% if culture.status == 'active' %}bg-success
                                {% elif culture.status == 'harvested' %}bg-primary
                                {% else %}bg-danger{% endif %}">
                                {{ culture.status_display }}
                            </span>
                        </div>
                        
                        <p class="text-muted mb-2">
                            <i class="fas fa-leaf"></i> {{ culture.crop_type.title() }}
                            {% if culture.variety %}
                                <br><small>{{ culture.variety }}</small>
                            {% endif %}
                        </p>
                        
                        <div class="row text-center mb-3">
                            <div class="col-6">
                                <strong>{{ culture.area_hectares }}</strong>
                                <br><small class="text-muted">hectares</small>
                            </div>
                            <div class="col-6">
                                <strong>{{ culture.days_since_planting }}</strong>
                                <br><small class="text-muted">dias plantado</small>
                            </div>
                        </div>
                        
                        {% if culture.location %}
                        <p class="text-muted mb-2">
                            <i class="fas fa-map-marker-alt"></i> {{ culture.location }}
                        </p>
                        {% endif %}
                        
                        <div class="d-flex justify-content-between">
                            <a href="{{ url_for('cultures.detail', id=culture.id) }}" 
                               class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-eye"></i> Ver
                            </a>
                            <a href="{{ url_for('cultures.edit', id=culture.id) }}" 
                               class="btn btn-outline-secondary btn-sm">
                                <i class="fas fa-edit"></i> Editar
                            </a>
                        </div>
                    </div>
                    
                    <div class="card-footer text-muted">
                        <small>Plantado em {{ culture.planting_date.strftime('%d/%m/%Y') }}</small>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Paginação -->
        {% if cultures.pages > 1 %}
        <nav aria-label="Paginação de culturas">
            <ul class="pagination justify-content-center">
                {% if cultures.has_prev %}
                    <li class="page-item">
                        <a class="page-link" href="{{ url_for('cultures.index', page=cultures.prev_num, search=search, status=status_filter) }}">
                            Anterior
                        </a>
                    </li>
                {% endif %}
                
                {% for page_num in cultures.iter_pages() %}
                    {% if page_num %}
                        {% if page_num != cultures.page %}
                            <li class="page-item">
                                <a class="page-link" href="{{ url_for('cultures.index', page=page_num, search=search, status=status_filter) }}">
                                    {{ page_num }}
                                </a>
                            </li>
                        {% else %}
                            <li class="page-item active">
                                <span class="page-link">{{ page_num }}</span>
                            </li>
                        {% endif %}
                    {% else %}
                        <li class="page-item disabled">
                            <span class="page-link">…</span>
                        </li>
                    {% endif %}
                {% endfor %}
                
                {% if cultures.has_next %}
                    <li class="page-item">
                        <a class="page-link" href="{{ url_for('cultures.index', page=cultures.next_num, search=search, status=status_filter) }}">
                            Próxima
                        </a>
                    </li>
                {% endif %}
            </ul>
        </nav>
        {% endif %}
        
    {% else %}
        <!-- Estado vazio -->
        <div class="text-center py-5">
            <i class="fas fa-seedling fa-4x text-muted mb-3"></i>
            <h3 class="text-muted">Nenhuma cultura encontrada</h3>
            {% if search or status_filter %}
                <p>Tente ajustar os filtros de busca.</p>
                <a href="{{ url_for('cultures.index') }}" class="btn btn-outline-primary">
                    Limpar Filtros
                </a>
            {% else %}
                <p>Comece adicionando sua primeira cultura!</p>
                <a href="{{ url_for('cultures.new') }}" class="btn btn-success">
                    <i class="fas fa-plus"></i> Adicionar Primeira Cultura
                </a>
            {% endif %}
        </div>
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script>
// Atualizar estatísticas via AJAX (opcional)
function updateStats() {
    fetch('{{ url_for("cultures.api_stats") }}')
        .then(response => response.json())
        .then(data => {
            // Atualizar contadores se necessário
            console.log('Stats atualizadas:', data);
        })
        .catch(error => console.error('Erro ao atualizar stats:', error));
}

// Confirmar exclusão
function confirmDelete(cultureId, cultureName) {
    if (confirm(`Tem certeza que deseja excluir a cultura "${cultureName}"?`)) {
        // Criar form e submeter
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/cultures/${cultureId}/delete`;
        
        // CSRF token se necessário
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = csrfToken.content;
            form.appendChild(input);
        }
        
        document.body.appendChild(form);
        form.submit();
    }
}
</script>
{% endblock %}
```

### TEMPLATE DE FORMULÁRIO

```html
<!-- templates/cultures/form.html -->
{% extends "base.html" %}

{% block title %}{{ title }} - AgTech Portugal{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h4 class="mb-0">
                        <i class="fas fa-seedling text-success"></i> {{ title }}
                    </h4>
                </div>
                
                <div class="card-body">
                    <form method="POST" novalidate>
                        {{ form.hidden_tag() }}
                        
                        <!-- Dados básicos -->
                        <div class="row mb-3">
                            <div class="col-md-8">
                                <label for="{{ form.name.id }}" class="form-label">
                                    {{ form.name.label.text }} <span class="text-danger">*</span>
                                </label>
                                {{ form.name(class="form-control" + (" is-invalid" if form.name.errors else "")) }}
                                {% if form.name.errors %}
                                    <div class="invalid-feedback">
                                        {{ form.name.errors[0] }}
                                    </div>
                                {% endif %}
                            </div>
                            <div class="col-md-4">
                                <label for="{{ form.area_hectares.id }}" class="form-label">
                                    {{ form.area_hectares.label.text }} <span class="text-danger">*</span>
                                </label>
                                {{ form.area_hectares(class="form-control" + (" is-invalid" if form.area_hectares.errors else "")) }}
                                {% if form.area_hectares.errors %}
                                    <div class="invalid-feedback">
                                        {{ form.area_hectares.errors[0] }}
                                    </div>
                                {% endif %}
                            </div>
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="{{ form.crop_type.id }}" class="form-label">
                                    {{ form.crop_type.label.text }} <span class="text-danger">*</span>
                                </label>
                                {{ form.crop_type(class="form-select" + (" is-invalid" if form.crop_type.errors else "")) }}
                                {% if form.crop_type.errors %}
                                    <div class="invalid-feedback">
                                        {{ form.crop_type.errors[0] }}
                                    </div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label for="{{ form.variety.id }}" class="form-label">
                                    {{ form.variety.label.text }}
                                </label>
                                {{ form.variety(class="form-control") }}
                            </div>
                        </div>
                        
                        <!-- Localização -->
                        <div class="row mb-3">
                            <div class="col-md-8">
                                <label for="{{ form.location.id }}" class="form-label">
                                    {{ form.location.label.text }}
                                </label>
                                {{ form.location(class="form-control") }}
                            </div>
                            <div class="col-md-4">
                                <label for="{{ form.field_name.id }}" class="form-label">
                                    {{ form.field_name.label.text }}
                                </label>
                                {{ form.field_name(class="form-control") }}
                            </div>
                        </div>
                        
                        <!-- Datas -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="{{ form.planting_date.id }}" class="form-label">
                                    {{ form.planting_date.label.text }} <span class="text-danger">*</span>
                                </label>
                                {{ form.planting_date(class="form-control" + (" is-invalid" if form.planting_date.errors else "")) }}
                                {% if form.planting_date.errors %}
                                    <div class="invalid-feedback">
                                        {{ form.planting_date.errors[0] }}
                                    </div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label for="{{ form.expected_harvest_date.id }}" class="form-label">
                                    {{ form.expected_harvest_date.label.text }}
                                </label>
                                {{ form.expected_harvest_date(class="form-control" + (" is-invalid" if form.expected_harvest_date.errors else "")) }}
                                {% if form.expected_harvest_date.errors %}
                                    <div class="invalid-feedback">
                                        {{ form.expected_harvest_date.errors[0] }}
                                    </div>
                                {% endif %}
                            </div>
                        </div>
                        
                        <!-- Status e estágio -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="{{ form.status.id }}" class="form-label">
                                    {{ form.status.label.text }} <span class="text-danger">*</span>
                                </label>
                                {{ form.status(class="form-select") }}
                            </div>
                            <div class="col-md-6">
                                <label for="{{ form.growth_stage.id }}" class="form-label">
                                    {{ form.growth_stage.label.text }}
                                </label>
                                {{ form.growth_stage(class="form-select") }}
                            </div>
                        </div>
                        
                        <!-- Produção estimada -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label for="{{ form.estimated_yield.id }}" class="form-label">
                                    {{ form.estimated_yield.label.text }}
                                </label>
                                {{ form.estimated_yield(class="form-control") }}
                            </div>
                        </div>
                        
                        <!-- Observações -->
                        <div class="mb-3">
                            <label for="{{ form.notes.id }}" class="form-label">
                                {{ form.notes.label.text }}
                            </label>
                            {{ form.notes(class="form-control") }}
                        </div>
                        
                        <!-- Botões -->
                        <div class="d-flex justify-content-between">
                            <a href="{{ url_for('cultures.index') }}" class="btn btn-secondary">
                                <i class="fas fa-arrow-left"></i> Voltar
                            </a>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save"></i> 
                                {% if culture %}Atualizar{% else %}Cadastrar{% endif %}
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
// Calcular data de colheita estimada baseada no tipo de cultura
document.getElementById('{{ form.crop_type.id }}').addEventListener('change', function() {
    const plantingDate = document.getElementById('{{ form.planting_date.id }}').value;
    const harvestDate = document.getElementById('{{ form.expected_harvest_date.id }}');
    
    if (plantingDate && !harvestDate.value) {
        const planting = new Date(plantingDate);
        let daysToAdd = 90; // padrão
        
        // Estimativas por tipo de cultura
        const cropDays = {
            'cereais': 120,
            'leguminosas': 90,
            'hortícolas': 60,
            'frutícolas': 365,
            'forragens': 45,
            'oleaginosas': 100
        };
        
        daysToAdd = cropDays[this.value] || 90;
        
        const harvest = new Date(planting);
        harvest.setDate(harvest.getDate() + daysToAdd);
        
        harvestDate.value = harvest.toISOString().split('T')[0];
    }
});
</script>
{% endblock %}
```

---

## ✅ CRITÉRIOS DE VALIDAÇÃO

### TESTES OBRIGATÓRIOS

**1. Funcionalidade Básica:**
- [ ] Rota `/cultures` carrega sem redirecionamento
- [ ] Lista culturas do usuário logado apenas
- [ ] Formulário de cadastro funcional
- [ ] Edição de culturas existentes
- [ ] Exclusão com confirmação
- [ ] Paginação funciona com muitas culturas

**2. Validações:**
- [ ] Campos obrigatórios validados
- [ ] Área deve ser > 0
- [ ] Data de colheita posterior ao plantio
- [ ] Usuário só vê suas próprias culturas

**3. Interface:**
- [ ] Design responsivo (mobile/desktop)
- [ ] Filtros e busca funcionais
- [ ] Estatísticas atualizadas
- [ ] Mensagens de feedback claras

**4. Integração:**
- [ ] Dashboard principal atualizado
- [ ] Contadores refletem dados reais
- [ ] API endpoints funcionais

### SCRIPT DE TESTE

```python
# test_cultures.py
import requests
from datetime import date, timedelta

def test_cultures_functionality():
    base_url = "http://localhost:5000"
    
    # Login
    session = requests.Session()
    login_data = {
        'email': 'teste.final.sprint1@agrotech.pt',
        'password': 'TesteFinalSprint2025!'
    }
    session.post(f"{base_url}/auth/login", data=login_data)
    
    # Teste 1: Acessar página de culturas
    response = session.get(f"{base_url}/cultures")
    assert response.status_code == 200, "Página de culturas inacessível"
    
    # Teste 2: Cadastrar cultura
    culture_data = {
        'name': 'Milho Teste',
        'crop_type': 'cereais',
        'area_hectares': 1.5,
        'planting_date': date.today().isoformat(),
        'status': 'active'
    }
    response = session.post(f"{base_url}/cultures/new", data=culture_data)
    assert response.status_code in [200, 302], "Cadastro de cultura falhou"
    
    # Teste 3: API de estatísticas
    response = session.get(f"{base_url}/cultures/api/stats")
    assert response.status_code == 200, "API de stats falhou"
    
    print("✅ Todos os testes de culturas passaram!")

if __name__ == "__main__":
    test_cultures_functionality()
```

---

## 📦 ENTREGÁVEIS OBRIGATÓRIOS

### 1. CÓDIGO BACKEND
- [ ] `app/models/culture.py` - Modelo completo
- [ ] `app/cultures/routes.py` - Controller com CRUD
- [ ] `app/cultures/forms.py` - Formulários WTForms
- [ ] Migration para criar tabela cultures

### 2. TEMPLATES FRONTEND
- [ ] `templates/cultures/index.html` - Listagem
- [ ] `templates/cultures/form.html` - Cadastro/edição
- [ ] `templates/cultures/detail.html` - Detalhes
- [ ] CSS customizado para culturas

### 3. INTEGRAÇÃO
- [ ] Blueprint registrado em `app/__init__.py`
- [ ] Menu de navegação atualizado
- [ ] Dashboard com dados reais
- [ ] API endpoints funcionais

### 4. TESTES E DOCUMENTAÇÃO
- [ ] Testes unitários básicos
- [ ] Script de validação
- [ ] Documentação da API
- [ ] Exemplos de uso

---

## 🚀 RESULTADO ESPERADO

### ANTES DA IMPLEMENTAÇÃO
- Funcionalidade Culturas: 0%
- Dashboard: Dados fake/placeholder
- Rota /cultures: Inacessível

### APÓS A IMPLEMENTAÇÃO
- Funcionalidade Culturas: 100%
- Dashboard: Dados reais das culturas
- Score Sprint 3: +25% (de 50% para 75%)

### VALIDAÇÃO FINAL
```bash
# Teste manual
1. Acessar https://www.agenteagricola.com/cultures
2. Cadastrar nova cultura
3. Verificar dashboard atualizado
4. Testar edição e exclusão

# Teste automatizado
python3 validacao_automatizada_sprint3.py
# Resultado esperado: cultures_functionality: 100%
```

---

**🌱 Esta implementação transformará o AgroTech Portugal em uma ferramenta real de gestão agrícola, substituindo dados fake por funcionalidade genuína para agricultores familiares portugueses!**

