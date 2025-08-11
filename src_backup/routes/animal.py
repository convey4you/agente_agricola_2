"""
Rotas de animais
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from datetime import datetime, date
from ..models.animal import Animal
from .. import db

animal_bp = Blueprint('animal', __name__, url_prefix='/api/animais')

@animal_bp.route('/', methods=['GET'])
@login_required
def listar_animais():
    """Lista todos os animais do usuário"""
    animais = Animal.query.filter_by(user_id=current_user.id).all()
    
    if request.is_json:
        return jsonify({
            'animais': [animal.to_dict() for animal in animais]
        })
    
    return render_template('animais/lista.html', animais=animais)

@animal_bp.route('/', methods=['POST'])
@login_required
def criar_animal():
    """Cria um novo animal"""
    data = request.get_json() if request.is_json else request.form
    
    # Validação básica
    if not data.get('nome') or not data.get('especie'):
        return jsonify({'error': 'Nome e espécie são obrigatórios'}), 400
    
    # Converter datas se fornecidas
    data_nascimento = None
    data_aquisicao = None
    
    if data.get('data_nascimento'):
        try:
            data_nascimento = datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data de nascimento inválido'}), 400
    
    if data.get('data_aquisicao'):
        try:
            data_aquisicao = datetime.strptime(data.get('data_aquisicao'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data de aquisição inválido'}), 400
    
    animal = Animal(
        nome=data.get('nome'),
        especie=data.get('especie'),
        raca=data.get('raca'),
        sexo=data.get('sexo'),
        idade=int(data.get('idade')) if data.get('idade') else None,
        peso=float(data.get('peso')) if data.get('peso') else None,
        data_nascimento=data_nascimento,
        data_aquisicao=data_aquisicao,
        valor_aquisicao=float(data.get('valor_aquisicao')) if data.get('valor_aquisicao') else None,
        status=data.get('status', 'ativo'),
        identificacao=data.get('identificacao'),
        observacoes=data.get('observacoes'),
        user_id=current_user.id
    )
    
    try:
        db.session.add(animal)
        db.session.commit()
        
        return jsonify({
            'message': 'Animal criado com sucesso',
            'animal': animal.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar animal'}), 500

@animal_bp.route('/<int:animal_id>', methods=['GET'])
@login_required
def obter_animal(animal_id):
    """Obtém um animal específico"""
    animal = Animal.query.filter_by(id=animal_id, user_id=current_user.id).first()
    
    if not animal:
        return jsonify({'error': 'Animal não encontrado'}), 404
    
    return jsonify({
        'animal': animal.to_dict()
    })

@animal_bp.route('/<int:animal_id>', methods=['PUT'])
@login_required
def atualizar_animal(animal_id):
    """Atualiza um animal"""
    animal = Animal.query.filter_by(id=animal_id, user_id=current_user.id).first()
    
    if not animal:
        return jsonify({'error': 'Animal não encontrado'}), 404
    
    data = request.get_json() if request.is_json else request.form
    
    # Atualizar campos
    if 'nome' in data:
        animal.nome = data['nome']
    if 'especie' in data:
        animal.especie = data['especie']
    if 'raca' in data:
        animal.raca = data['raca']
    if 'sexo' in data:
        animal.sexo = data['sexo']
    if 'idade' in data:
        animal.idade = int(data['idade']) if data['idade'] else None
    if 'peso' in data:
        animal.peso = float(data['peso']) if data['peso'] else None
    if 'status' in data:
        animal.status = data['status']
    if 'identificacao' in data:
        animal.identificacao = data['identificacao']
    if 'observacoes' in data:
        animal.observacoes = data['observacoes']
    
    # Datas
    if 'data_nascimento' in data:
        try:
            animal.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if data['data_nascimento'] else None
        except ValueError:
            return jsonify({'error': 'Formato de data de nascimento inválido'}), 400
    
    if 'data_aquisicao' in data:
        try:
            animal.data_aquisicao = datetime.strptime(data['data_aquisicao'], '%Y-%m-%d').date() if data['data_aquisicao'] else None
        except ValueError:
            return jsonify({'error': 'Formato de data de aquisição inválido'}), 400
    
    if 'valor_aquisicao' in data:
        animal.valor_aquisicao = float(data['valor_aquisicao']) if data['valor_aquisicao'] else None
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Animal atualizado com sucesso',
            'animal': animal.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar animal'}), 500

@animal_bp.route('/<int:animal_id>', methods=['DELETE'])
@login_required
def deletar_animal(animal_id):
    """Deleta um animal"""
    animal = Animal.query.filter_by(id=animal_id, user_id=current_user.id).first()
    
    if not animal:
        return jsonify({'error': 'Animal não encontrado'}), 404
    
    try:
        db.session.delete(animal)
        db.session.commit()
        
        return jsonify({
            'message': 'Animal deletado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar animal'}), 500

@animal_bp.route('/especies', methods=['GET'])
@login_required
def listar_especies():
    """Lista as espécies disponíveis"""
    especies = [
        'Bovino',
        'Suíno',
        'Aves',
        'Ovino',
        'Caprino',
        'Equino',
        'Peixe',
        'Coelho',
        'Outro'
    ]
    
    return jsonify({
        'especies': especies
    })
