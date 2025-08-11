"""
Marketplace Service - Lógica de negócio para o marketplace
"""
from flask import current_app
from flask_login import current_user
from app import db
from app.models.marketplace import MarketplaceItem


class MarketplaceService:
    """Serviço para gerenciar operações do marketplace"""
    
    @staticmethod
    def get_items_list(page=1, per_page=20, category=None, search=None):
        """Obter lista paginada de itens do marketplace"""
        try:
            # Construir query base
            query = MarketplaceItem.query.filter_by(status='active')
            
            # Aplicar filtros
            if category:
                query = query.filter_by(category=category)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    MarketplaceItem.title.ilike(search_term) |
                    MarketplaceItem.description.ilike(search_term)
                )
            
            # Ordenar e paginar
            items = query.order_by(
                MarketplaceItem.featured.desc(),
                MarketplaceItem.created_at.desc()
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'success': True,
                'data': {
                    'items': [item.to_dict() for item in items.items],
                    'total': items.total,
                    'pages': items.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': items.has_next,
                    'has_prev': items.has_prev
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao listar itens do marketplace: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar itens do marketplace'
            }
    
    @staticmethod
    def create_marketplace_item(data):
        """Criar novo item no marketplace"""
        try:
            # Criar item
            item = MarketplaceItem(
                seller_id=current_user.id,
                title=data['title'],
                description=data.get('description'),
                category=data['category'],
                subcategory=data.get('subcategory'),
                price=float(data['price']),
                currency=data.get('currency', 'BRL'),
                quantity_available=data.get('quantity_available', 1),
                unit=data.get('unit'),
                condition=data.get('condition', 'new'),
                location_city=data.get('location_city', current_user.cidade),
                location_state=data.get('location_state', current_user.estado),
                shipping_available=data.get('shipping_available', False),
                pickup_available=data.get('pickup_available', True),
                images=data.get('images', []),
                status='active'
            )
            
            db.session.add(item)
            db.session.commit()
            
            return {
                'success': True,
                'data': {
                    'message': 'Item criado com sucesso',
                    'item': item.to_dict()
                }
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': f'Erro de validação: {str(e)}'
            }
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao criar item: {e}")
            return {
                'success': False,
                'error': 'Erro interno ao criar item'
            }
    
    @staticmethod
    def get_item_details(item_id, increment_view=True):
        """Obter detalhes de um item específico"""
        try:
            item = MarketplaceItem.query.filter_by(
                id=item_id,
                status='active'
            ).first()
            
            if not item:
                return {
                    'success': False,
                    'error': 'Item não encontrado'
                }
            
            # Incrementar contador de visualizações se solicitado
            if increment_view:
                item.views_count += 1
                db.session.commit()
            
            return {
                'success': True,
                'data': {
                    'item': item.to_dict()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter item {item_id}: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar item'
            }
    
    @staticmethod
    def get_user_items():
        """Obter itens do usuário logado"""
        try:
            items = MarketplaceItem.query.filter_by(
                seller_id=current_user.id
            ).order_by(
                MarketplaceItem.created_at.desc()
            ).all()
            
            # Separar por status para melhor organização
            active_items = [item.to_dict() for item in items if item.status == 'active']
            inactive_items = [item.to_dict() for item in items if item.status != 'active']
            
            return {
                'success': True,
                'data': {
                    'items': [item.to_dict() for item in items],
                    'active_items': active_items,
                    'inactive_items': inactive_items,
                    'total_items': len(items),
                    'active_count': len(active_items),
                    'inactive_count': len(inactive_items)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter itens do usuário: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar seus itens'
            }
    
    @staticmethod
    def update_marketplace_item(item_id, data):
        """Atualizar item do marketplace"""
        try:
            item = MarketplaceItem.query.filter_by(
                id=item_id,
                seller_id=current_user.id
            ).first()
            
            if not item:
                return {
                    'success': False,
                    'error': 'Item não encontrado ou sem permissão'
                }
            
            # Atualizar campos permitidos
            allowed_fields = [
                'title', 'description', 'category', 'subcategory', 'price',
                'currency', 'quantity_available', 'unit', 'condition',
                'location_city', 'location_state', 'shipping_available',
                'pickup_available', 'images'
            ]
            
            for field in allowed_fields:
                if field in data:
                    if field == 'price':
                        setattr(item, field, float(data[field]))
                    else:
                        setattr(item, field, data[field])
            
            db.session.commit()
            
            return {
                'success': True,
                'data': {
                    'message': 'Item atualizado com sucesso',
                    'item': item.to_dict()
                }
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': f'Erro de validação: {str(e)}'
            }
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao atualizar item {item_id}: {e}")
            return {
                'success': False,
                'error': 'Erro interno ao atualizar item'
            }
    
    @staticmethod
    def delete_marketplace_item(item_id, soft_delete=True):
        """Deletar item do marketplace"""
        try:
            item = MarketplaceItem.query.filter_by(
                id=item_id,
                seller_id=current_user.id
            ).first()
            
            if not item:
                return {
                    'success': False,
                    'error': 'Item não encontrado ou sem permissão'
                }
            
            if soft_delete:
                # Soft delete - apenas marca como inativo
                item.status = 'inactive'
                db.session.commit()
                message = 'Item desativado com sucesso'
            else:
                # Hard delete - remove do banco
                db.session.delete(item)
                db.session.commit()
                message = 'Item removido permanentemente'
            
            return {
                'success': True,
                'data': {
                    'message': message
                }
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao deletar item {item_id}: {e}")
            return {
                'success': False,
                'error': 'Erro interno ao deletar item'
            }
    
    @staticmethod
    def get_categories():
        """Obter categorias disponíveis"""
        try:
            categories = [
                {'value': 'produtos', 'label': 'Produtos Agrícolas', 'icon': '🌾'},
                {'value': 'sementes', 'label': 'Sementes e Mudas', 'icon': '🌱'},
                {'value': 'ferramentas', 'label': 'Ferramentas', 'icon': '🔨'},
                {'value': 'equipamentos', 'label': 'Equipamentos', 'icon': '🚜'},
                {'value': 'insumos', 'label': 'Insumos', 'icon': '🧪'},
                {'value': 'servicos', 'label': 'Serviços', 'icon': '⚙️'},
                {'value': 'animais', 'label': 'Animais', 'icon': '🐄'},
                {'value': 'outros', 'label': 'Outros', 'icon': '📦'}
            ]
            
            return {
                'success': True,
                'data': {
                    'categories': categories
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter categorias: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar categorias'
            }
    
    @staticmethod
    def search_items(query_params):
        """Busca avançada de itens"""
        try:
            # Parâmetros de busca
            search = query_params.get('q', '')
            category = query_params.get('category')
            min_price = query_params.get('min_price', type=float)
            max_price = query_params.get('max_price', type=float)
            condition = query_params.get('condition')
            location_city = query_params.get('city')
            location_state = query_params.get('state')
            shipping = query_params.get('shipping', type=bool)
            pickup = query_params.get('pickup', type=bool)
            page = query_params.get('page', 1, type=int)
            per_page = query_params.get('per_page', 20, type=int)
            sort_by = query_params.get('sort', 'created_at')
            sort_order = query_params.get('order', 'desc')
            
            # Construir query
            query = MarketplaceItem.query.filter_by(status='active')
            
            # Aplicar filtros
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    MarketplaceItem.title.ilike(search_term) |
                    MarketplaceItem.description.ilike(search_term)
                )
            
            if category:
                query = query.filter_by(category=category)
            
            if min_price is not None:
                query = query.filter(MarketplaceItem.price >= min_price)
            
            if max_price is not None:
                query = query.filter(MarketplaceItem.price <= max_price)
            
            if condition:
                query = query.filter_by(condition=condition)
            
            if location_city:
                query = query.filter_by(location_city=location_city)
            
            if location_state:
                query = query.filter_by(location_state=location_state)
            
            if shipping is not None:
                query = query.filter_by(shipping_available=shipping)
            
            if pickup is not None:
                query = query.filter_by(pickup_available=pickup)
            
            # Aplicar ordenação
            sort_column = getattr(MarketplaceItem, sort_by, MarketplaceItem.created_at)
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            
            # Paginar
            items = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'data': {
                    'items': [item.to_dict() for item in items.items],
                    'total': items.total,
                    'pages': items.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': items.has_next,
                    'has_prev': items.has_prev,
                    'search_params': query_params
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro na busca de itens: {e}")
            return {
                'success': False,
                'error': 'Erro ao realizar busca'
            }
    
    @staticmethod
    def get_featured_items(limit=10):
        """Obter itens em destaque"""
        try:
            items = MarketplaceItem.query.filter_by(
                status='active',
                featured=True
            ).order_by(
                MarketplaceItem.created_at.desc()
            ).limit(limit).all()
            
            return {
                'success': True,
                'data': {
                    'items': [item.to_dict() for item in items]
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter itens em destaque: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar itens em destaque'
            }
    
    @staticmethod
    def get_marketplace_stats():
        """Obter estatísticas do marketplace"""
        try:
            total_items = MarketplaceItem.query.filter_by(status='active').count()
            total_categories = db.session.query(MarketplaceItem.category).distinct().count()
            
            # Estatísticas por categoria
            category_stats = db.session.query(
                MarketplaceItem.category,
                db.func.count(MarketplaceItem.id).label('count')
            ).filter_by(status='active').group_by(MarketplaceItem.category).all()
            
            return {
                'success': True,
                'data': {
                    'total_items': total_items,
                    'total_categories': total_categories,
                    'category_stats': [
                        {'category': stat.category, 'count': stat.count}
                        for stat in category_stats
                    ]
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'success': False,
                'error': 'Erro ao carregar estatísticas'
            }
