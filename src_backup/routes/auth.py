"""
Rotas de autenticação
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..models.user import User
from .. import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login do usuário"""
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        if request.is_json:
            return jsonify({'error': 'Email e password são obrigatórios'}), 400
        flash('Email e password são obrigatórios', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        login_user(user)
        if request.is_json:
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user': user.to_dict()
            })
        return redirect(url_for('index'))
    
    if request.is_json:
        return jsonify({'error': 'Credenciais inválidas'}), 401
    flash('Credenciais inválidas', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de novo usuário"""
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json() if request.is_json else request.form
    email = data.get('email')
    password = data.get('password')
    telefone = data.get('telefone')
    endereco = data.get('endereco')
    
    if not email or not password:
        if request.is_json:
            return jsonify({'error': 'Email e password são obrigatórios'}), 400
        flash('Email e password são obrigatórios', 'error')
        return redirect(url_for('auth.register'))
    
    # Verificar se usuário já existe
    if User.query.filter_by(email=email).first():
        if request.is_json:
            return jsonify({'error': 'Email já existe'}), 400
        flash('Email já existe', 'error')
        return redirect(url_for('auth.register'))
    
    # Criar novo usuário
    user = User(
        email=email,
        telefone=telefone,
        endereco=endereco
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Usuário criado com sucesso',
                'user': user.to_dict()
            }), 201
        
        flash('Usuário criado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Erro ao criar usuário'}), 500
        flash('Erro ao criar usuário', 'error')
        return redirect(url_for('auth.register'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    if request.is_json:
        return jsonify({'message': 'Logout realizado com sucesso'})
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    if request.is_json:
        return jsonify({
            'user': current_user.to_dict()
        })
    return render_template('profile.html', user=current_user)
