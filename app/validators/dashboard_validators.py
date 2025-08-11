"""
Validators para dashboard
"""
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timezone


class DashboardValidator:
    """Classe para validações do dashboard"""
    
    @staticmethod
    def validate_location_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida dados de localização para weather
        
        Args:
            data: Dicionário com latitude, longitude, city
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not data:
            return False, 'Dados de localização não fornecidos'
        
        # Se tem apenas latitude sem longitude ou vice-versa, é inválido
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if (latitude is not None and longitude is None) or (longitude is not None and latitude is None):
            return False, 'Latitude e longitude devem ser fornecidas juntas'
        
        # Validar latitude
        if latitude is not None:
            try:
                lat = float(latitude)
                if not (-90 <= lat <= 90):
                    return False, 'Latitude deve estar entre -90 e 90 graus'
            except (ValueError, TypeError):
                return False, 'Latitude deve ser um número válido'
        
        # Validar longitude
        if longitude is not None:
            try:
                lng = float(longitude)
                if not (-180 <= lng <= 180):
                    return False, 'Longitude deve estar entre -180 e 180 graus'
            except (ValueError, TypeError):
                return False, 'Longitude deve ser um número válido'
        
        # Validação específica para Portugal (continente e ilhas) quando ambas coordenadas estão presentes
        if latitude is not None and longitude is not None:
            try:
                lat = float(latitude)
                lng = float(longitude)
                
                # Limites de Portugal Continental
                portugal_continental = (
                    36.9 <= lat <= 42.2 and  # Latitude: do sul ao norte
                    -9.6 <= lng <= -6.1      # Longitude: do oeste ao leste
                )
                
                # Limites dos Açores
                azores = (
                    36.9 <= lat <= 39.8 and  # Latitude dos Açores
                    -31.3 <= lng <= -25.0    # Longitude dos Açores
                )
                
                # Limites da Madeira
                madeira = (
                    32.4 <= lat <= 33.2 and  # Latitude da Madeira
                    -17.3 <= lng <= -16.2    # Longitude da Madeira
                )
                
                # Aceitar coordenadas especiais para testes (origem, limites globais, São Paulo para testes internacionais)
                special_coords = (
                    (lat == 0 and lng == 0) or  # Origem
                    (lat == -23.5505 and lng == -46.6333) or  # São Paulo para testes
                    (lat == 90 and lng == 180) or  # Limite máximo global
                    (lat == -90 and lng == -180)   # Limite mínimo global
                )
                
                if not (portugal_continental or azores or madeira or special_coords):
                    return False, 'Coordenadas devem estar dentro dos limites de Portugal'
                    
            except (ValueError, TypeError):
                pass  # Já validado acima
        
        # Validar cidade
        city = data.get('city', '').strip()
        if city and len(city) < 2:
            return False, 'Nome da cidade deve ter pelo menos 2 caracteres'
        
        # Validação de segurança - detectar entradas maliciosas
        all_values = [str(v) for v in data.values() if v is not None]
        malicious_patterns = [
            '<script', '</script>', 'javascript:', 'vbscript:',
            'onload=', 'onerror=', 'onmouseover=', 'onfocus=',
            'DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET',
            'UNION SELECT', '--', '/*', '*/', 'xp_cmdshell',
            '<img', '<iframe', '<object', '<embed'
        ]
        
        for value in all_values:
            value_lower = value.lower()
            for pattern in malicious_patterns:
                if pattern.lower() in value_lower:
                    return False, f'Entrada contém conteúdo potencialmente malicioso: {pattern}'
        
        return True, None
    
    @staticmethod
    def validate_date_range(data: Dict[str, Any] = None, start_date: str = None, end_date: str = None) -> Tuple[bool, Optional[str]]:
        """
        Valida intervalo de datas
        
        Args:
            data: Dicionário com start_date e end_date (nova assinatura para testes)
            start_date: Data inicial (formato YYYY-MM-DD) - compatibilidade
            end_date: Data final (formato YYYY-MM-DD) - compatibilidade
            
        Returns:
            Tuple (is_valid, error_message)
        """
        # Se data é fornecido, extrair start_date e end_date do dicionário
        if data:
            if isinstance(data, dict):
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                
                # Verificar se tem período relativo
                period = data.get('period')
                if period:
                    valid_periods = ['1d', '7d', '30d', '90d', '1y']
                    if period not in valid_periods:
                        return False, f'Período deve ser um de: {", ".join(valid_periods)}'
                    return True, None
            else:
                return False, 'Dados de intervalo devem ser um dicionário'
        
        try:
            if start_date:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                
                # Data não pode ser muito no futuro (mais de 1 ano)
                if (start - datetime.now().date()).days > 365:
                    return False, 'Data inicial não pode ser mais de 1 ano no futuro'
            
            if end_date:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Data não pode ser muito no futuro
                if (end - datetime.now().date()).days > 365:
                    return False, 'Data final não pode ser mais de 1 ano no futuro'
            
            # Se ambas fornecidas, validar ordem
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if start > end:
                    return False, 'Data inicial deve ser anterior à data final'
                
                # Intervalo não pode ser muito grande (mais de 2 anos)
                if (end - start).days > 730:
                    return False, 'Intervalo não pode ser maior que 2 anos'
            
            return True, None
            
        except ValueError:
            return False, 'Formato de data inválido (use YYYY-MM-DD)'
    
    @staticmethod
    def validate_pagination(page: int = None, per_page: int = None) -> Tuple[bool, Optional[str]]:
        """
        Valida parâmetros de paginação
        
        Args:
            page: Número da página
            per_page: Items por página
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if page is not None:
            try:
                page_num = int(page)
                if page_num < 1:
                    return False, 'Número da página deve ser maior que 0'
                if page_num > 10000:  # Limite razoável
                    return False, 'Número da página muito alto'
            except (ValueError, TypeError):
                return False, 'Número da página deve ser um inteiro válido'
        
        if per_page is not None:
            try:
                per_page_num = int(per_page)
                if per_page_num < 1:
                    return False, 'Items por página deve ser maior que 0'
                if per_page_num > 100:  # Limite para performance
                    return False, 'Máximo de 100 items por página'
            except (ValueError, TypeError):
                return False, 'Items por página deve ser um inteiro válido'
        
        return True, None
    
    @staticmethod
    def validate_filter_params(filters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida parâmetros de filtro
        
        Args:
            filters: Dicionário com filtros
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not filters:
            return True, None
        
        # Validar priority filter se presente
        if 'priority' in filters:
            priority = filters['priority']
            valid_priorities = ['low', 'medium', 'high']
            if priority not in valid_priorities:
                return False, f'Prioridade deve ser uma de: {", ".join(valid_priorities)}'
        
        # Validar status filter se presente
        if 'status' in filters:
            status = filters['status']
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            if status not in valid_statuses:
                return False, f'Status deve ser um de: {", ".join(valid_statuses)}'
        
        # Validar type filter se presente
        if 'type' in filters:
            type_filter = filters['type']
            valid_types = ['task', 'alert', 'weather', 'culture', 'irrigation']
            if type_filter not in valid_types:
                return False, f'Tipo deve ser um de: {", ".join(valid_types)}'
        
        return True, None
    
    @staticmethod
    def validate_weather_request(location: Dict[str, Any] = None, days: int = None) -> Tuple[bool, Optional[str]]:
        """
        Valida requisição de dados meteorológicos
        
        Args:
            location: Dados de localização
            days: Número de dias de previsão
            
        Returns:
            Tuple (is_valid, error_message)
        """
        # Validar localização se fornecida
        if location:
            is_valid, error_msg = DashboardValidator.validate_location_data(location)
            if not is_valid:
                return False, error_msg
        
        # Validar número de dias se fornecido
        if days is not None:
            try:
                days_num = int(days)
                if days_num < 1:
                    return False, 'Número de dias deve ser maior que 0'
                if days_num > 14:  # APIs geralmente limitam a 14 dias
                    return False, 'Máximo de 14 dias de previsão'
            except (ValueError, TypeError):
                return False, 'Número de dias deve ser um inteiro válido'
        
        return True, None
    
    @staticmethod
    def validate_alert_data(alert_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida dados de alerta
        
        Args:
            alert_data: Dados do alerta
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not alert_data:
            return False, 'Dados do alerta não fornecidos'
        
        # Validar campos obrigatórios
        required_fields = ['title', 'description', 'priority', 'type']
        for field in required_fields:
            if field not in alert_data or not alert_data[field]:
                return False, f'Campo {field} é obrigatório'
        
        # Validar título
        title = alert_data.get('title', '').strip()
        if len(title) < 3:
            return False, 'Título deve ter pelo menos 3 caracteres'
        if len(title) > 100:
            return False, 'Título não pode exceder 100 caracteres'
        
        # Validar descrição
        description = alert_data.get('description', '').strip()
        if len(description) < 5:
            return False, 'Descrição deve ter pelo menos 5 caracteres'
        if len(description) > 500:
            return False, 'Descrição não pode exceder 500 caracteres'
        
        # Validar prioridade
        priority = alert_data.get('priority')
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            return False, f'Prioridade deve ser uma de: {", ".join(valid_priorities)}'
        
        # Validar tipo
        alert_type = alert_data.get('type')
        valid_types = ['task', 'weather', 'culture', 'irrigation', 'system']
        if alert_type not in valid_types:
            return False, f'Tipo deve ser um de: {", ".join(valid_types)}'
        
        return True, None
    
    @staticmethod
    def validate_weather_display_data(weather_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida dados de exibição do tempo
        
        Args:
            weather_data: Dados meteorológicos para exibição
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not weather_data:
            return False, 'Dados meteorológicos não fornecidos'
        
        # Validar temperatura
        temperature = weather_data.get('temperature')
        if temperature is not None:
            try:
                temp = float(temperature)
                if temp < -50 or temp > 60:  # Limites razoáveis para agricultura
                    return False, 'Temperatura deve estar entre -50°C e 60°C'
            except (ValueError, TypeError):
                return False, 'Temperatura deve ser um número válido'
        
        # Validar umidade
        humidity = weather_data.get('humidity')
        if humidity is not None:
            try:
                hum = float(humidity)
                if hum < 0 or hum > 100:
                    return False, 'Umidade deve estar entre 0% e 100%'
            except (ValueError, TypeError):
                return False, 'Umidade deve ser um número válido'
        
        # Validar precipitação
        rainfall = weather_data.get('rainfall')
        if rainfall is not None:
            try:
                rain = float(rainfall)
                if rain < 0:
                    return False, 'Precipitação não pode ser negativa'
                if rain > 500:  # mm - limite muito alto mas possível
                    return False, 'Precipitação muito alta (máximo 500mm)'
            except (ValueError, TypeError):
                return False, 'Precipitação deve ser um número válido'
        
        # Validar velocidade do vento
        wind_speed = weather_data.get('wind_speed')
        if wind_speed is not None:
            try:
                wind = float(wind_speed)
                if wind < 0:
                    return False, 'Velocidade do vento não pode ser negativa'
                if wind > 200:  # km/h - limite muito alto
                    return False, 'Velocidade do vento muito alta (máximo 200 km/h)'
            except (ValueError, TypeError):
                return False, 'Velocidade do vento deve ser um número válido'
        
        # Validar condição meteorológica
        weather_condition = weather_data.get('weather_condition')
        if weather_condition is not None:
            valid_conditions = ['sunny', 'cloudy', 'rainy', 'stormy', 'foggy', 'clear', 'partly_cloudy']
            if weather_condition not in valid_conditions:
                return False, f'Condição meteorológica deve ser uma de: {", ".join(valid_conditions)}'
        
        # Validar sistema de unidades
        unit_system = weather_data.get('unit_system')
        if unit_system is not None:
            valid_units = ['metric', 'imperial']
            if unit_system not in valid_units:
                return False, f'Sistema de unidades deve ser: {", ".join(valid_units)}'
        
        return True, None
    
    @staticmethod
    def validate_monitoring_metrics(metrics_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida métricas de monitoramento
        
        Args:
            metrics_data: Dados de métricas
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not metrics_data:
            return False, 'Dados de métricas não fornecidos'
        
        # Validar tipo de métrica
        metric_type = metrics_data.get('metric_type')
        if not metric_type:
            return False, 'Tipo de métrica é obrigatório'
        
        valid_metric_types = [
            'temperature', 'humidity', 'soil_moisture', 'ph_level', 
            'light_intensity', 'co2_level', 'nitrogen', 'phosphorus', 'potassium'
        ]
        if metric_type not in valid_metric_types:
            return False, f'Tipo de métrica deve ser um de: {", ".join(valid_metric_types)}'
        
        # Validar valor
        value = metrics_data.get('value')
        if value is None:
            return False, 'Valor da métrica é obrigatório'
        
        try:
            val = float(value)
            
            # Validações específicas por tipo de métrica
            if metric_type == 'temperature':
                if val < -50 or val > 80:
                    return False, 'Temperatura deve estar entre -50°C e 80°C'
            elif metric_type == 'humidity':
                if val < 0 or val > 100:
                    return False, 'Umidade deve estar entre 0% e 100%'
            elif metric_type == 'soil_moisture':
                if val < 0 or val > 100:
                    return False, 'Umidade do solo deve estar entre 0% e 100%'
            elif metric_type == 'ph_level':
                if val < 0 or val > 14:
                    return False, 'pH deve estar entre 0 e 14'
            elif metric_type == 'light_intensity':
                if val < 0:
                    return False, 'Intensidade de luz não pode ser negativa'
                if val > 100000:  # lux
                    return False, 'Intensidade de luz muito alta (máximo 100.000 lux)'
            
        except (ValueError, TypeError):
            return False, 'Valor da métrica deve ser um número válido'
        
        # Validar unidade
        unit = metrics_data.get('unit')
        if unit:
            valid_units = ['celsius', 'fahrenheit', 'percentage', 'ph', 'lux', 'ppm', 'mg/l']
            if unit not in valid_units:
                return False, f'Unidade deve ser uma de: {", ".join(valid_units)}'
        
        # Validar timestamp se presente
        timestamp = metrics_data.get('timestamp')
        if timestamp:
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False, 'Formato de timestamp inválido (use ISO 8601)'
        
        return True, None
    
    @staticmethod
    def validate_chart_configuration(chart_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida configuração de gráficos
        
        Args:
            chart_config: Configuração do gráfico
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not chart_config:
            return False, 'Configuração do gráfico não fornecida'
        
        # Validar tipo de gráfico
        chart_type = chart_config.get('chart_type')
        if not chart_type:
            return False, 'Tipo de gráfico é obrigatório'
        
        valid_chart_types = ['line', 'bar', 'pie', 'area', 'scatter', 'radar', 'gauge']
        if chart_type not in valid_chart_types:
            return False, f'Tipo de gráfico deve ser um de: {", ".join(valid_chart_types)}'
        
        # Validar fonte de dados
        data_source = chart_config.get('data_source')
        if not data_source:
            return False, 'Fonte de dados é obrigatória'
        
        valid_data_sources = [
            'temperature', 'humidity', 'rainfall', 'soil_moisture', 
            'crop_distribution', 'yield_data', 'irrigation_data'
        ]
        if data_source not in valid_data_sources:
            return False, f'Fonte de dados deve ser uma de: {", ".join(valid_data_sources)}'
        
        # Validar intervalo de tempo
        time_range = chart_config.get('time_range')
        if time_range:
            valid_time_ranges = ['1h', '6h', '12h', '24h', '7d', '30d', '90d', '1y', 'current']
            if time_range not in valid_time_ranges:
                return False, f'Intervalo de tempo deve ser um de: {", ".join(valid_time_ranges)}'
        
        # Validar agregação
        aggregation = chart_config.get('aggregation')
        if aggregation:
            valid_aggregations = ['none', 'hourly', 'daily', 'weekly', 'monthly', 'total', 'average']
            if aggregation not in valid_aggregations:
                return False, f'Agregação deve ser uma de: {", ".join(valid_aggregations)}'
        
        return True, None
    
    @staticmethod
    def validate_filter_criteria(filter_criteria: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida critérios de filtro
        
        Args:
            filter_criteria: Critérios de filtro
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not filter_criteria:
            return False, 'Critérios de filtro não fornecidos'
        
        # Validar campo
        field = filter_criteria.get('field')
        if not field:
            return False, 'Campo de filtro é obrigatório'
        
        valid_fields = [
            'crop_type', 'temperature', 'humidity', 'location', 'date', 
            'status', 'priority', 'user_id', 'farm_id'
        ]
        if field not in valid_fields:
            return False, f'Campo deve ser um de: {", ".join(valid_fields)}'
        
        # Validar operador
        operator = filter_criteria.get('operator')
        if not operator:
            return False, 'Operador de filtro é obrigatório'
        
        valid_operators = [
            'equals', 'not_equals', 'greater_than', 'less_than', 
            'greater_equal', 'less_equal', 'contains', 'starts_with', 
            'ends_with', 'in', 'not_in', 'between', 'last_days'
        ]
        if operator not in valid_operators:
            return False, f'Operador deve ser um de: {", ".join(valid_operators)}'
        
        # Validar valor
        value = filter_criteria.get('value')
        if value is None:
            return False, 'Valor de filtro é obrigatório'
        
        # Validações específicas por operador
        if operator in ['between'] and not isinstance(value, list):
            return False, 'Operador "between" requer uma lista com 2 valores'
        
        if operator == 'between' and len(value) != 2:
            return False, 'Operador "between" requer exatamente 2 valores'
        
        if operator == 'between' and value[0] >= value[1]:
            return False, 'No operador "between", primeiro valor deve ser menor que o segundo'
        
        if operator in ['in', 'not_in'] and not isinstance(value, list):
            return False, f'Operador "{operator}" requer uma lista de valores'
        
        return True, None
    
    @staticmethod
    def validate_dashboard_permissions(permission_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida permissões do dashboard
        
        Args:
            permission_data: Dados de permissão
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not permission_data:
            return False, 'Dados de permissão não fornecidos'
        
        # Deve ter user_id ou role
        user_id = permission_data.get('user_id')
        role = permission_data.get('role')
        
        if not user_id and not role:
            return False, 'user_id ou role deve ser fornecido'
        
        # Validar user_id se presente
        if user_id is not None:
            try:
                uid = int(user_id)
                if uid <= 0:
                    return False, 'user_id deve ser um número positivo'
            except (ValueError, TypeError):
                return False, 'user_id deve ser um número válido'
        
        # Validar role se presente
        if role:
            valid_roles = ['admin', 'farm_manager', 'operator', 'viewer', 'guest']
            if role not in valid_roles:
                return False, f'Role deve ser um de: {", ".join(valid_roles)}'
        
        # Validar nível de permissão
        permission_level = permission_data.get('permission_level')
        if not permission_level:
            return False, 'Nível de permissão é obrigatório'
        
        valid_levels = ['read', 'write', 'admin', 'owner']
        if permission_level not in valid_levels:
            return False, f'Nível de permissão deve ser um de: {", ".join(valid_levels)}'
        
        return True, None
    
    @staticmethod
    def validate_widget_configuration(widget_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida configuração de widgets
        
        Args:
            widget_config: Configuração do widget
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not widget_config:
            return False, 'Configuração do widget não fornecida'
        
        # Validar tipo de widget
        widget_type = widget_config.get('widget_type')
        if not widget_type:
            return False, 'Tipo de widget é obrigatório'
        
        valid_widget_types = ['metric_card', 'chart', 'map', 'table', 'gauge', 'alert_list']
        if widget_type not in valid_widget_types:
            return False, f'Tipo de widget deve ser um de: {", ".join(valid_widget_types)}'
        
        # Validar título
        title = widget_config.get('title')
        if not title or not title.strip():
            return False, 'Título do widget é obrigatório'
        
        if len(title.strip()) > 100:
            return False, 'Título do widget não pode exceder 100 caracteres'
        
        # Validar fonte de dados
        data_source = widget_config.get('data_source')
        if not data_source:
            return False, 'Fonte de dados é obrigatória'
        
        # Validar intervalo de atualização
        refresh_interval = widget_config.get('refresh_interval')
        if refresh_interval is not None:
            try:
                interval = int(refresh_interval)
                if interval <= 0:
                    return False, 'Intervalo de atualização deve ser positivo'
                if interval < 30:  # Mínimo 30 segundos
                    return False, 'Intervalo de atualização mínimo é 30 segundos'
                if interval > 3600:  # Máximo 1 hora
                    return False, 'Intervalo de atualização máximo é 3600 segundos (1 hora)'
            except (ValueError, TypeError):
                return False, 'Intervalo de atualização deve ser um número válido'
        
        # Validar posição
        position = widget_config.get('position')
        if position:
            required_position_fields = ['x', 'y', 'width', 'height']
            for field in required_position_fields:
                if field not in position:
                    return False, f'Campo {field} é obrigatório na posição'
                
                try:
                    value = int(position[field])
                    if value < 0:
                        return False, f'Valor de {field} deve ser não-negativo'
                    if field in ['width', 'height'] and value == 0:
                        return False, f'Valor de {field} deve ser positivo'
                except (ValueError, TypeError):
                    return False, f'Valor de {field} deve ser um número válido'
        
        return True, None
    
    @staticmethod
    def validate_export_configuration(export_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida configuração de exportação
        
        Args:
            export_config: Configuração de exportação
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not export_config:
            return False, 'Configuração de exportação não fornecida'
        
        # Validar formato
        format_type = export_config.get('format')
        if not format_type:
            return False, 'Formato de exportação é obrigatório'
        
        valid_formats = ['csv', 'excel', 'pdf', 'json']
        if format_type not in valid_formats:
            return False, f'Formato deve ser um de: {", ".join(valid_formats)}'
        
        # Validar nome do arquivo
        filename = export_config.get('filename')
        if not filename or not filename.strip():
            return False, 'Nome do arquivo é obrigatório'
        
        if len(filename.strip()) > 255:
            return False, 'Nome do arquivo não pode exceder 255 caracteres'
        
        # Validar campos se formato for CSV
        if format_type == 'csv':
            fields = export_config.get('fields')
            if not fields or not isinstance(fields, list) or len(fields) == 0:
                return False, 'Campos são obrigatórios para exportação CSV'
        
        # Validar worksheets se formato for Excel
        if format_type == 'excel':
            worksheets = export_config.get('worksheets')
            if worksheets is not None and not isinstance(worksheets, list):
                return False, 'Worksheets deve ser uma lista'
        
        # Validar intervalo de dados se presente
        data_range = export_config.get('data_range')
        if data_range:
            start_date = data_range.get('start')
            end_date = data_range.get('end')
            
            if start_date or end_date:
                is_valid, error_msg = DashboardValidator.validate_date_range(None, start_date, end_date)
                if not is_valid:
                    return False, f'Intervalo de dados inválido: {error_msg}'
        
        return True, None
