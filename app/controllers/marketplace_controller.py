"""
Marketplace Controller - Rotas do marketplace (Refatorado)
Segue padrões SOLID com separação de responsabilidades
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

# Services e Validators
from app.services.marketplace_service import MarketplaceService
from app.validators.marketplace_validators import MarketplaceValidator

# Utilitários compartilhados
from app.utils.response_helpers import ResponseHandler
from app.utils.logging_helpers import LoggingHelper

marketplace_bp = Blueprint('marketplace', __name__)


@marketplace_bp.route('/', methods=['GET'])
def list_items():
    """Página principal do marketplace - Renderiza interface"""
    try:
        LoggingHelper.log_request('marketplace.list_items', 'GET')
        
        # Se é uma requisição AJAX/API, retornar JSON
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('api') == 'true':
            # Obter parâmetros da requisição
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            category = request.args.get('category')
            search = request.args.get('search')
            
            # Validar parâmetros de paginação
            is_valid, error_msg = MarketplaceValidator.validate_pagination(page, per_page)
            if not is_valid:
                return ResponseHandler.handle_validation_error(error_msg)
            
            # Validar categoria se fornecida
            if category:
                is_valid, error_msg = MarketplaceValidator.validate_category(category)
                if not is_valid:
                    return ResponseHandler.handle_validation_error(error_msg)
            
            # Validar termo de busca se fornecido
            if search:
                is_valid, error_msg = MarketplaceValidator.validate_search_term(search)
                if not is_valid:
                    return ResponseHandler.handle_validation_error(error_msg)
            
            # Obter itens através do service
            result = MarketplaceService.get_items_list(page, per_page, category, search)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'products': result.get('items', []),
                    'pagination': result.get('pagination', {}),
                    'count': len(result.get('items', []))
                })
            else:
                return ResponseHandler.handle_service_error(result.get('error', 'Erro desconhecido'))
        
        # Caso contrário, renderizar template
        return render_template('marketplace/index.html')
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.list_items')
        return ResponseHandler.handle_server_error('Erro ao listar itens do marketplace')


@marketplace_bp.route('/', methods=['POST'])
@login_required
def create_item():
    """Criar novo item no marketplace - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.create_item', 'POST', current_user.email)
        
        data = request.get_json()
        
        # Validar dados de criação
        is_valid, error_msg = MarketplaceValidator.validate_item_creation_data(data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Criar item através do service
        result = MarketplaceService.create_marketplace_item(data)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'MARKETPLACE_ITEM_CREATED',
                {'item_id': result['data']['item']['id']}
            )
            return ResponseHandler.handle_success(result['data'], 201)
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.create_item')
        return ResponseHandler.handle_server_error('Erro ao criar item')


@marketplace_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Obter item específico - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.get_item', 'GET')
        
        # Validar ID do item
        is_valid, error_msg = MarketplaceValidator.validate_item_id(item_id)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Obter item através do service
        result = MarketplaceService.get_item_details(item_id, increment_view=True)
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_not_found(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.get_item')
        return ResponseHandler.handle_server_error('Erro ao obter item')


@marketplace_bp.route('/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Atualizar item do marketplace - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.update_item', 'PUT', current_user.email)
        
        # Validar ID do item
        is_valid, error_msg = MarketplaceValidator.validate_item_id(item_id)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        data = request.get_json()
        
        # Validar dados de atualização
        is_valid, error_msg = MarketplaceValidator.validate_update_data(data)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Atualizar item através do service
        result = MarketplaceService.update_marketplace_item(item_id, data)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'MARKETPLACE_ITEM_UPDATED',
                {'item_id': item_id}
            )
            return ResponseHandler.handle_success(result['data'])
        else:
            if 'não encontrado' in result['error'] or 'sem permissão' in result['error']:
                return ResponseHandler.handle_not_found(result['error'])
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.update_item')
        return ResponseHandler.handle_server_error('Erro ao atualizar item')


@marketplace_bp.route('/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Deletar item do marketplace - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.delete_item', 'DELETE', current_user.email)
        
        # Validar ID do item
        is_valid, error_msg = MarketplaceValidator.validate_item_id(item_id)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Verificar se é soft delete ou hard delete
        hard_delete = request.args.get('hard', 'false').lower() == 'true'
        
        # Deletar item através do service
        result = MarketplaceService.delete_marketplace_item(item_id, soft_delete=not hard_delete)
        
        if result['success']:
            LoggingHelper.log_user_action(
                current_user.email, 
                'MARKETPLACE_ITEM_DELETED',
                {'item_id': item_id, 'hard_delete': hard_delete}
            )
            return ResponseHandler.handle_success(result['data'])
        else:
            if 'não encontrado' in result['error'] or 'sem permissão' in result['error']:
                return ResponseHandler.handle_not_found(result['error'])
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.delete_item')
        return ResponseHandler.handle_server_error('Erro ao deletar item')


@marketplace_bp.route('/my-items', methods=['GET'])
@login_required
def my_items():
    """Itens do usuário logado - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.my_items', 'GET', current_user.email)
        
        # Obter itens do usuário através do service
        result = MarketplaceService.get_user_items()
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.my_items')
        return ResponseHandler.handle_server_error('Erro ao obter seus itens')


@marketplace_bp.route('/categories', methods=['GET'])
def get_categories():
    """Obter categorias disponíveis - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.get_categories', 'GET')
        
        # Obter categorias através do service
        result = MarketplaceService.get_categories()
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.get_categories')
        return ResponseHandler.handle_server_error('Erro ao obter categorias')


@marketplace_bp.route('/search', methods=['GET'])
def search_items():
    """Busca avançada de itens - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.search_items', 'GET')
        
        # Obter todos os parâmetros de busca
        query_params = request.args.to_dict()
        
        # Validar parâmetros específicos
        page = query_params.get('page', 1, type=int)
        per_page = query_params.get('per_page', 20, type=int)
        
        is_valid, error_msg = MarketplaceValidator.validate_pagination(page, per_page)
        if not is_valid:
            return ResponseHandler.handle_validation_error(error_msg)
        
        # Validar faixa de preço se fornecida
        min_price = query_params.get('min_price', type=float)
        max_price = query_params.get('max_price', type=float)
        
        if min_price is not None or max_price is not None:
            is_valid, error_msg = MarketplaceValidator.validate_price_range(min_price, max_price)
            if not is_valid:
                return ResponseHandler.handle_validation_error(error_msg)
        
        # Validar parâmetros de ordenação
        sort_by = query_params.get('sort')
        sort_order = query_params.get('order')
        
        if sort_by or sort_order:
            is_valid, error_msg = MarketplaceValidator.validate_sort_params(sort_by, sort_order)
            if not is_valid:
                return ResponseHandler.handle_validation_error(error_msg)
        
        # Realizar busca através do service
        result = MarketplaceService.search_items(query_params)
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.search_items')
        return ResponseHandler.handle_server_error('Erro ao realizar busca')


@marketplace_bp.route('/featured', methods=['GET'])
def get_featured_items():
    """Obter itens em destaque - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.get_featured_items', 'GET')
        
        # Obter limite se fornecido
        limit = request.args.get('limit', 10, type=int)
        
        # Validar limite
        if limit < 1 or limit > 50:
            return ResponseHandler.handle_validation_error(
                'Limite deve ser entre 1 e 50'
            )
        
        # Obter itens em destaque através do service
        result = MarketplaceService.get_featured_items(limit)
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.get_featured_items')
        return ResponseHandler.handle_server_error('Erro ao obter itens em destaque')


@marketplace_bp.route('/stats', methods=['GET'])
def get_marketplace_stats():
    """Obter estatísticas do marketplace - Refatorado"""
    try:
        LoggingHelper.log_request('marketplace.get_stats', 'GET')
        
        # Obter estatísticas através do service
        result = MarketplaceService.get_marketplace_stats()
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.get_stats')
        return ResponseHandler.handle_server_error('Erro ao obter estatísticas')


# === NOVAS ROTAS API PARA FRONTEND ===

@marketplace_bp.route('/api/products', methods=['GET'])
def api_get_products():
    """API para buscar produtos - compatibilidade com frontend"""
    try:
        LoggingHelper.log_request('marketplace.api_get_products', 'GET')
        
        # Filtros da query string
        filters = {
            'category': request.args.get('category'),
            'location': request.args.get('location'),
            'search': request.args.get('search'),
            'organic': request.args.get('organic') == 'true'
        }
        
        # Remover filtros vazios
        filters = {k: v for k, v in filters.items() if v and v != 'false'}
        
        # Por enquanto, retornar produtos demo
        demo_products = [
            {
                'id': 1,
                'name': 'Tomates Frescos',
                'category': 'hortalicas',
                'price': 2.50,
                'unit': 'kg',
                'location': 'Lisboa',
                'organic': True,
                'delivery': True,
                'description': 'Tomates frescos cultivados em estufa, sem pesticidas.',
                'seller': 'João Silva',
                'contact': '(+351) 912 345 678',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'name': 'Alface Hidropónica',
                'category': 'hortalicas',
                'price': 1.80,
                'unit': 'unidade',
                'location': 'Porto',
                'organic': False,
                'delivery': False,
                'description': 'Alface cultivada em sistema hidropónico.',
                'seller': 'Maria Santos',
                'contact': 'maria@exemplo.pt',
                'created_at': '2024-01-14T15:20:00Z'
            },
            {
                'id': 3,
                'name': 'Mel de Eucalipto',
                'category': 'outros',
                'price': 8.50,
                'unit': 'kg',
                'location': 'Coimbra',
                'organic': True,
                'delivery': True,
                'description': 'Mel puro de eucalipto, produção própria.',
                'seller': 'António Costa',
                'contact': '(+351) 967 123 456',
                'created_at': '2024-01-13T09:15:00Z'
            },
            {
                'id': 4,
                'name': 'Cenouras Biológicas',
                'category': 'hortalicas',
                'price': 1.90,
                'unit': 'kg',
                'location': 'Braga',
                'organic': True,
                'delivery': True,
                'description': 'Cenouras cultivadas sem químicos, solo rico.',
                'seller': 'Carlos Pereira',
                'contact': '(+351) 933 456 789',
                'created_at': '2024-01-12T14:45:00Z'
            },
            {
                'id': 5,
                'name': 'Arado Pequeno',
                'category': 'equipamentos',
                'price': 250.00,
                'unit': 'unidade',
                'location': 'Aveiro',
                'organic': False,
                'delivery': True,
                'description': 'Arado manual em bom estado, ideal para hortas pequenas.',
                'seller': 'Fernando Oliveira',
                'contact': 'fernando@agricultura.pt',
                'created_at': '2024-01-11T11:30:00Z'
            }
        ]
        
        # Aplicar filtros simples
        filtered_products = demo_products
        
        if filters.get('category'):
            filtered_products = [p for p in filtered_products if p['category'] == filters['category']]
        
        if filters.get('location'):
            filtered_products = [p for p in filtered_products if filters['location'].lower() in p['location'].lower()]
        
        if filters.get('search'):
            search_term = filters['search'].lower()
            filtered_products = [p for p in filtered_products if 
                               search_term in p['name'].lower() or 
                               search_term in p.get('description', '').lower()]
        
        if filters.get('organic'):
            filtered_products = [p for p in filtered_products if p.get('organic', False)]
        
        return jsonify({
            'success': True,
            'products': filtered_products,
            'count': len(filtered_products)
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.api_get_products')
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar produtos'
        }), 500


@marketplace_bp.route('/api/categories', methods=['GET'])
def api_get_categories():
    """API para listar categorias disponíveis"""
    try:
        categories = [
            {'id': 'hortalicas', 'name': 'Hortaliças', 'icon': '🥬'},
            {'id': 'frutas', 'name': 'Frutas', 'icon': '🍎'},
            {'id': 'cereais', 'name': 'Cereais', 'icon': '🌾'},
            {'id': 'equipamentos', 'name': 'Equipamentos', 'icon': '🚜'},
            {'id': 'sementes', 'name': 'Sementes', 'icon': '🌱'},
            {'id': 'fertilizantes', 'name': 'Fertilizantes', 'icon': '🧪'},
            {'id': 'outros', 'name': 'Outros', 'icon': '📦'}
        ]
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.api_get_categories')
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar categorias'
        }), 500


@marketplace_bp.route('/api/products', methods=['POST'])
@login_required
def api_create_product():
    """API para criar produto"""
    try:
        LoggingHelper.log_request('marketplace.api_create_product', 'POST')
        
        # Simular criação bem-sucedida por enquanto
        return jsonify({
            'success': True,
            'product_id': 999,
            'message': 'Produto criado com sucesso (modo demo)'
        })
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.api_create_product')
        return jsonify({
            'success': False,
            'error': 'Erro ao criar produto'
        }), 500
        
        # Obter estatísticas através do service
        result = MarketplaceService.get_marketplace_stats()
        
        if result['success']:
            return ResponseHandler.handle_success(result['data'])
        else:
            return ResponseHandler.handle_server_error(result['error'])
        
    except Exception as e:
        LoggingHelper.log_error(e, 'marketplace.get_stats')
        return ResponseHandler.handle_server_error('Erro ao obter estatísticas')


# === FIM DOS CONTROLLERS REFATORADOS ===
