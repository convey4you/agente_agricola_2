"""
Marketplace Validators - Validações para o marketplace
"""
import re
from decimal import Decimal, InvalidOperation


class MarketplaceValidator:
    """Classe para validações relacionadas ao marketplace"""
    
    @staticmethod
    def validate_pagination(page=None, per_page=None):
        """Validar parâmetros de paginação"""
        if page is not None:
            if not isinstance(page, int) or page < 1:
                return False, "Página deve ser um número positivo"
        
        if per_page is not None:
            if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
                return False, "Itens por página deve ser entre 1 e 100"
        
        return True, None
    
    @staticmethod
    def validate_category(category):
        """Validar categoria"""
        if not category:
            return True, None  # Categoria é opcional para listagem
        
        valid_categories = [
            'produtos', 'sementes', 'ferramentas', 'equipamentos',
            'insumos', 'servicos', 'animais', 'outros'
        ]
        
        if category not in valid_categories:
            return False, f"Categoria inválida. Use: {', '.join(valid_categories)}"
        
        return True, None
    
    @staticmethod
    def validate_search_term(search):
        """Validar termo de busca"""
        if not search:
            return True, None  # Busca é opcional
        
        if not isinstance(search, str):
            return False, "Termo de busca deve ser uma string"
        
        if len(search.strip()) < 2:
            return False, "Termo de busca deve ter pelo menos 2 caracteres"
        
        if len(search) > 100:
            return False, "Termo de busca deve ter no máximo 100 caracteres"
        
        return True, None
    
    @staticmethod
    def validate_item_creation_data(data):
        """Validar dados para criação de item"""
        if not data:
            return False, "Dados não fornecidos"
        
        if not isinstance(data, dict):
            return False, "Dados devem ser um objeto JSON"
        
        # Campos obrigatórios
        required_fields = ['title', 'category', 'price']
        for field in required_fields:
            if not data.get(field):
                return False, f"Campo {field} é obrigatório"
        
        # Validar título
        title = data.get('title', '').strip()
        if len(title) < 5:
            return False, "Título deve ter pelo menos 5 caracteres"
        if len(title) > 200:
            return False, "Título deve ter no máximo 200 caracteres"
        
        # Validar categoria
        is_valid, error_msg = MarketplaceValidator.validate_category(data.get('category'))
        if not is_valid:
            return False, error_msg
        
        # Validar preço
        try:
            price = float(data.get('price', 0))
            if price <= 0:
                return False, "Preço deve ser maior que zero"
            if price > 999999.99:
                return False, "Preço muito alto (máximo: R$ 999.999,99)"
        except (ValueError, TypeError):
            return False, "Preço deve ser um número válido"
        
        # Validar quantidade disponível
        quantity = data.get('quantity_available', 1)
        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity < 0:
                    return False, "Quantidade deve ser zero ou positiva"
                if quantity > 99999:
                    return False, "Quantidade muito alta (máximo: 99.999)"
            except (ValueError, TypeError):
                return False, "Quantidade deve ser um número inteiro"
        
        # Validar descrição se fornecida
        description = data.get('description')
        if description:
            if len(description) > 2000:
                return False, "Descrição deve ter no máximo 2000 caracteres"
        
        # Validar condição
        condition = data.get('condition', 'new')
        valid_conditions = ['new', 'used', 'refurbished']
        if condition not in valid_conditions:
            return False, f"Condição inválida. Use: {', '.join(valid_conditions)}"
        
        # Validar moeda
        currency = data.get('currency', 'BRL')
        valid_currencies = ['BRL', 'USD', 'EUR']
        if currency not in valid_currencies:
            return False, f"Moeda inválida. Use: {', '.join(valid_currencies)}"
        
        # Validar imagens se fornecidas
        images = data.get('images', [])
        if images:
            if not isinstance(images, list):
                return False, "Imagens devem ser uma lista"
            if len(images) > 10:
                return False, "Máximo 10 imagens por item"
            
            for i, image_url in enumerate(images):
                if not isinstance(image_url, str):
                    return False, f"Imagem {i+1} deve ser uma URL válida"
                if len(image_url) > 500:
                    return False, f"URL da imagem {i+1} muito longa"
        
        return True, None
    
    @staticmethod
    def validate_item_id(item_id):
        """Validar ID de item"""
        if not item_id:
            return False, "ID do item é obrigatório"
        
        if not isinstance(item_id, int) or item_id <= 0:
            return False, "ID do item deve ser um número positivo"
        
        return True, None
    
    @staticmethod
    def validate_price_range(min_price=None, max_price=None):
        """Validar faixa de preço"""
        if min_price is not None:
            try:
                min_price = float(min_price)
                if min_price < 0:
                    return False, "Preço mínimo não pode ser negativo"
            except (ValueError, TypeError):
                return False, "Preço mínimo deve ser um número válido"
        
        if max_price is not None:
            try:
                max_price = float(max_price)
                if max_price <= 0:
                    return False, "Preço máximo deve ser maior que zero"
            except (ValueError, TypeError):
                return False, "Preço máximo deve ser um número válido"
        
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                return False, "Preço mínimo não pode ser maior que o máximo"
        
        return True, None
    
    @staticmethod
    def validate_location(city=None, state=None):
        """Validar localização"""
        if city:
            if not isinstance(city, str):
                return False, "Cidade deve ser uma string"
            if len(city.strip()) < 2:
                return False, "Nome da cidade deve ter pelo menos 2 caracteres"
            if len(city) > 100:
                return False, "Nome da cidade muito longo"
            # Verificar se contém apenas letras, espaços e alguns caracteres especiais
            if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', city):
                return False, "Nome da cidade contém caracteres inválidos"
        
        if state:
            if not isinstance(state, str):
                return False, "Estado deve ser uma string"
            if len(state.strip()) < 2:
                return False, "Nome do estado deve ter pelo menos 2 caracteres"
            if len(state) > 50:
                return False, "Nome do estado muito longo"
            if not re.match(r'^[a-zA-ZÀ-ÿ\s\-]+$', state):
                return False, "Nome do estado contém caracteres inválidos"
        
        return True, None
    
    @staticmethod
    def validate_sort_params(sort_by=None, sort_order=None):
        """Validar parâmetros de ordenação"""
        if sort_by:
            valid_sort_fields = [
                'created_at', 'price', 'title', 'views_count', 'featured'
            ]
            if sort_by not in valid_sort_fields:
                return False, f"Campo de ordenação inválido. Use: {', '.join(valid_sort_fields)}"
        
        if sort_order:
            if not isinstance(sort_order, str):
                return False, "Ordem deve ser uma string"
            valid_orders = ['asc', 'desc']
            if sort_order.lower() not in valid_orders:
                return False, f"Ordem inválida. Use: {', '.join(valid_orders)}"
        
        return True, None
    
    @staticmethod
    def validate_boolean_params(**params):
        """Validar parâmetros booleanos"""
        for param_name, param_value in params.items():
            if param_value is not None:
                if not isinstance(param_value, bool):
                    return False, f"Parâmetro {param_name} deve ser true ou false"
        
        return True, None
    
    @staticmethod
    def validate_condition(condition):
        """Validar condição do item"""
        if not condition:
            return True, None  # Condição é opcional
        
        valid_conditions = ['new', 'used', 'refurbished']
        if condition not in valid_conditions:
            return False, f"Condição inválida. Use: {', '.join(valid_conditions)}"
        
        return True, None
    
    @staticmethod
    def validate_unit(unit):
        """Validar unidade de medida"""
        if not unit:
            return True, None  # Unidade é opcional
        
        valid_units = [
            'kg', 'g', 'ton', 'l', 'ml', 'un', 'cx', 'pc', 'mt', 'cm',
            'ha', 'm2', 'pac', 'frd', 'dz', 'cen'
        ]
        
        if unit not in valid_units:
            return False, f"Unidade inválida. Use: {', '.join(valid_units)}"
        
        return True, None
    
    @staticmethod
    def validate_update_data(data):
        """Validar dados para atualização de item"""
        if not data:
            return False, "Nenhum dado fornecido para atualização"
        
        if not isinstance(data, dict):
            return False, "Dados devem ser um objeto JSON"
        
        # Se título fornecido, validar
        if 'title' in data:
            title = data['title'].strip() if data['title'] else ''
            if len(title) < 5:
                return False, "Título deve ter pelo menos 5 caracteres"
            if len(title) > 200:
                return False, "Título deve ter no máximo 200 caracteres"
        
        # Se categoria fornecida, validar
        if 'category' in data:
            is_valid, error_msg = MarketplaceValidator.validate_category(data['category'])
            if not is_valid:
                return False, error_msg
        
        # Se preço fornecido, validar
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return False, "Preço deve ser maior que zero"
                if price > 999999.99:
                    return False, "Preço muito alto (máximo: R$ 999.999,99)"
            except (ValueError, TypeError):
                return False, "Preço deve ser um número válido"
        
        # Se quantidade fornecida, validar
        if 'quantity_available' in data:
            try:
                quantity = int(data['quantity_available'])
                if quantity < 0:
                    return False, "Quantidade deve ser zero ou positiva"
                if quantity > 99999:
                    return False, "Quantidade muito alta (máximo: 99.999)"
            except (ValueError, TypeError):
                return False, "Quantidade deve ser um número inteiro"
        
        # Se condição fornecida, validar
        if 'condition' in data:
            is_valid, error_msg = MarketplaceValidator.validate_condition(data['condition'])
            if not is_valid:
                return False, error_msg
        
        # Se unidade fornecida, validar
        if 'unit' in data:
            is_valid, error_msg = MarketplaceValidator.validate_unit(data['unit'])
            if not is_valid:
                return False, error_msg
        
        return True, None
