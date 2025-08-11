"""
Rotas de tarefas
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from datetime import datetime
from ..models.tarefa import Tarefa
from ..models.cultura import Cultura
from ..models.animal import Animal
from .. import db

tarefa_bp = Blueprint('tarefa', __name__, url_prefix='/api/tarefas')

@tarefa_bp.route('/', methods=['GET'])
@login_required
def listar_tarefas():
    """Lista todas as tarefas do usuário"""
    status = request.args.get('status')
    tipo = request.args.get('tipo')
    
    query = Tarefa.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    tarefas = query.order_by(Tarefa.data_prevista.desc()).all()
    
    if request.is_json:
        return jsonify({
            'tarefas': [tarefa.to_dict() for tarefa in tarefas]
        })
    
    return render_template('tarefas/lista.html', tarefas=tarefas)

@tarefa_bp.route('/', methods=['POST'])
@login_required
def criar_tarefa():
    """Cria uma nova tarefa"""
    data = request.get_json() if request.is_json else request.form
    
    # Validação básica
    if not data.get('titulo') or not data.get('tipo'):
        return jsonify({'error': 'Título e tipo são obrigatórios'}), 400
    
    # Converter datas se fornecidas
    data_inicio = None
    data_fim = None
    data_prevista = None
    
    if data.get('data_inicio'):
        try:
            data_inicio = datetime.strptime(data.get('data_inicio'), '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'error': 'Formato de data de início inválido'}), 400
    
    if data.get('data_fim'):
        try:
            data_fim = datetime.strptime(data.get('data_fim'), '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'error': 'Formato de data de fim inválido'}), 400
    
    if data.get('data_prevista'):
        try:
            data_prevista = datetime.strptime(data.get('data_prevista'), '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'error': 'Formato de data prevista inválido'}), 400
    
    tarefa = Tarefa(
        titulo=data.get('titulo'),
        descricao=data.get('descricao'),
        tipo=data.get('tipo'),
        prioridade=data.get('prioridade', 'media'),
        status=data.get('status', 'pendente'),
        data_inicio=data_inicio,
        data_fim=data_fim,
        data_prevista=data_prevista,
        tempo_estimado=int(data.get('tempo_estimado')) if data.get('tempo_estimado') else None,
        custo_estimado=float(data.get('custo_estimado')) if data.get('custo_estimado') else None,
        observacoes=data.get('observacoes'),
        user_id=current_user.id,
        cultura_id=int(data.get('cultura_id')) if data.get('cultura_id') else None,
        animal_id=int(data.get('animal_id')) if data.get('animal_id') else None
    )
    
    try:
        db.session.add(tarefa)
        db.session.commit()
        
        return jsonify({
            'message': 'Tarefa criada com sucesso',
            'tarefa': tarefa.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar tarefa'}), 500

@tarefa_bp.route('/<int:tarefa_id>', methods=['GET'])
@login_required
def obter_tarefa(tarefa_id):
    """Obtém uma tarefa específica"""
    tarefa = Tarefa.query.filter_by(id=tarefa_id, user_id=current_user.id).first()
    
    if not tarefa:
        return jsonify({'error': 'Tarefa não encontrada'}), 404
    
    return jsonify({
        'tarefa': tarefa.to_dict()
    })

@tarefa_bp.route('/<int:tarefa_id>', methods=['PUT'])
@login_required
def atualizar_tarefa(tarefa_id):
    """Atualiza uma tarefa"""
    tarefa = Tarefa.query.filter_by(id=tarefa_id, user_id=current_user.id).first()
    
    if not tarefa:
        return jsonify({'error': 'Tarefa não encontrada'}), 404
    
    data = request.get_json() if request.is_json else request.form
    
    # Atualizar campos
    if 'titulo' in data:
        tarefa.titulo = data['titulo']
    if 'descricao' in data:
        tarefa.descricao = data['descricao']
    if 'tipo' in data:
        tarefa.tipo = data['tipo']
    if 'prioridade' in data:
        tarefa.prioridade = data['prioridade']
    if 'status' in data:
        tarefa.status = data['status']
    if 'observacoes' in data:
        tarefa.observacoes = data['observacoes']
    if 'tempo_estimado' in data:
        tarefa.tempo_estimado = int(data['tempo_estimado']) if data['tempo_estimado'] else None
    if 'tempo_real' in data:
        tarefa.tempo_real = int(data['tempo_real']) if data['tempo_real'] else None
    if 'custo_estimado' in data:
        tarefa.custo_estimado = float(data['custo_estimado']) if data['custo_estimado'] else None
    if 'custo_real' in data:
        tarefa.custo_real = float(data['custo_real']) if data['custo_real'] else None
    if 'cultura_id' in data:
        tarefa.cultura_id = int(data['cultura_id']) if data['cultura_id'] else None
    if 'animal_id' in data:
        tarefa.animal_id = int(data['animal_id']) if data['animal_id'] else None
    
    # Datas
    if 'data_inicio' in data:
        try:
            tarefa.data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%dT%H:%M') if data['data_inicio'] else None
        except ValueError:
            return jsonify({'error': 'Formato de data de início inválido'}), 400
    
    if 'data_fim' in data:
        try:
            tarefa.data_fim = datetime.strptime(data['data_fim'], '%Y-%m-%dT%H:%M') if data['data_fim'] else None
        except ValueError:
            return jsonify({'error': 'Formato de data de fim inválido'}), 400
    
    if 'data_prevista' in data:
        try:
            tarefa.data_prevista = datetime.strptime(data['data_prevista'], '%Y-%m-%dT%H:%M') if data['data_prevista'] else None
        except ValueError:
            return jsonify({'error': 'Formato de data prevista inválido'}), 400
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Tarefa atualizada com sucesso',
            'tarefa': tarefa.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar tarefa'}), 500

@tarefa_bp.route('/<int:tarefa_id>', methods=['DELETE'])
@login_required
def deletar_tarefa(tarefa_id):
    """Deleta uma tarefa"""
    tarefa = Tarefa.query.filter_by(id=tarefa_id, user_id=current_user.id).first()
    
    if not tarefa:
        return jsonify({'error': 'Tarefa não encontrada'}), 404
    
    try:
        db.session.delete(tarefa)
        db.session.commit()
        
        return jsonify({
            'message': 'Tarefa deletada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar tarefa'}), 500

@tarefa_bp.route('/tipos', methods=['GET'])
@login_required
def listar_tipos():
    """Lista os tipos de tarefa disponíveis"""
    tipos = [
        'Plantio',
        'Irrigação',
        'Adubação',
        'Pulverização',
        'Colheita',
        'Vacinação',
        'Alimentação',
        'Limpeza',
        'Manutenção',
        'Monitoramento',
        'Outro'
    ]
    
    return jsonify({
        'tipos': tipos
    })

@tarefa_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_tarefas():
    """Dashboard com estatísticas das tarefas"""
    total = Tarefa.query.filter_by(user_id=current_user.id).count()
    pendentes = Tarefa.query.filter_by(user_id=current_user.id, status='pendente').count()
    em_andamento = Tarefa.query.filter_by(user_id=current_user.id, status='em_andamento').count()
    concluidas = Tarefa.query.filter_by(user_id=current_user.id, status='concluida').count()
    
    # Tarefas atrasadas
    atrasadas = Tarefa.query.filter(
        Tarefa.user_id == current_user.id,
        Tarefa.status.in_(['pendente', 'em_andamento']),
        Tarefa.data_prevista < datetime.now()
    ).count()
    
    return jsonify({
        'estatisticas': {
            'total': total,
            'pendentes': pendentes,
            'em_andamento': em_andamento,
            'concluidas': concluidas,
            'atrasadas': atrasadas
        }
    })
