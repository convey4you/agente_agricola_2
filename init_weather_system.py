"""
Script de Inicialização do Sistema de Clima
Configura localizações padrão e executa primeira coleta
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app import create_app, db
from app.models.weather_history import WeatherLocation, WeatherData
from app.services.weather_collector import WeatherCollectorService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_weather_system():
    """
    Inicializa o sistema de clima com configurações padrão
    """
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("Iniciando configuração do sistema de clima...")
            
            # Criar tabelas se não existirem
            db.create_all()
            logger.info("Tabelas do banco de dados verificadas")
            
            # Configurar localizações padrão
            setup_default_locations()
            
            # Executar primeira coleta
            execute_initial_collection()
            
            logger.info("Sistema de clima inicializado com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            raise


def setup_default_locations():
    """
    Configura localizações padrão para Portugal
    """
    try:
        logger.info("Configurando localizações padrão...")
        
        # Localizações principais de Portugal
        default_locations = [
            {
                'name': 'Lisboa',
                'country': 'Portugal',
                'latitude': 38.7223,
                'longitude': -9.1393,
                'is_default': True
            },
            {
                'name': 'Porto',
                'country': 'Portugal', 
                'latitude': 41.1579,
                'longitude': -8.6291,
                'is_default': False
            },
            {
                'name': 'Coimbra',
                'country': 'Portugal',
                'latitude': 40.2033,
                'longitude': -8.4103,
                'is_default': False
            },
            {
                'name': 'Faro',
                'country': 'Portugal',
                'latitude': 37.0194,
                'longitude': -7.9322,
                'is_default': False
            },
            {
                'name': 'Braga',
                'country': 'Portugal',
                'latitude': 41.5518,
                'longitude': -8.4229,
                'is_default': False
            }
        ]
        
        locations_added = 0
        
        for loc_data in default_locations:
            # Verificar se já existe
            existing = WeatherLocation.query.filter_by(
                name=loc_data['name'],
                country=loc_data['country']
            ).first()
            
            if not existing:
                location = WeatherLocation(
                    name=loc_data['name'],
                    country=loc_data['country'],
                    latitude=loc_data['latitude'],
                    longitude=loc_data['longitude'],
                    is_default=loc_data['is_default'],
                    is_active=True
                )
                
                db.session.add(location)
                locations_added += 1
                logger.info(f"Localização adicionada: {loc_data['name']}")
            else:
                logger.info(f"Localização já existe: {loc_data['name']}")
        
        db.session.commit()
        logger.info(f"Configuração concluída: {locations_added} novas localizações adicionadas")
        
    except Exception as e:
        logger.error(f"Erro ao configurar localizações: {e}")
        db.session.rollback()
        raise


def execute_initial_collection():
    """
    Executa primeira coleta de dados
    """
    try:
        logger.info("Executando primeira coleta de dados...")
        
        # Verificar se há chave da API configurada
        from flask import current_app
        api_key = current_app.config.get('WEATHER_API_KEY')
        
        if not api_key:
            logger.warning("WEATHER_API_KEY não configurada. Definindo chave de exemplo...")
            logger.warning("Configure a chave real no arquivo .env ou config.py")
            return
        
        # Executar coleta
        result = WeatherCollectorService.collect_all_locations()
        
        if result['success']:
            logger.info(f"Primeira coleta concluída com sucesso!")
            logger.info(f"Localizações processadas: {result['locations_processed']}")
            
            if result['locations_failed'] > 0:
                logger.warning(f"Localizações com falha: {result['locations_failed']}")
                for error in result['errors']:
                    logger.warning(f"  - {error}")
        else:
            logger.error("Primeira coleta falhou")
            for error in result['errors']:
                logger.error(f"  - {error}")
        
    except Exception as e:
        logger.error(f"Erro na primeira coleta: {e}")


def verify_system():
    """
    Verifica se o sistema está funcionando corretamente
    """
    try:
        logger.info("Verificando sistema...")
        
        # Verificar localizações
        locations = WeatherLocation.get_active_locations()
        logger.info(f"Localizações ativas: {len(locations)}")
        
        # Verificar dados
        current_data = WeatherData.query.filter_by(is_current=True).count()
        logger.info(f"Registros de dados atuais: {current_data}")
        
        # Verificar qualidade dos dados
        latest_record = WeatherData.query.filter_by(is_current=True).first()
        if latest_record:
            logger.info(f"Último registro: {latest_record.location_name} - {latest_record.temperature}°C")
            logger.info(f"Qualidade dos dados: {latest_record.data_quality}")
        else:
            logger.warning("Nenhum dado atual encontrado")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação: {e}")
        return False


def show_status():
    """
    Mostra status atual do sistema
    """
    try:
        from app.services.weather_data_service import WeatherDataService
        
        logger.info("=== STATUS DO SISTEMA DE CLIMA ===")
        
        # Status dos dados
        freshness = WeatherDataService.get_data_freshness()
        logger.info(f"Status dos dados: {freshness['status']}")
        logger.info(f"Mensagem: {freshness['message']}")
        
        if freshness.get('last_collection'):
            logger.info(f"Última coleta: {freshness['last_collection']}")
        
        # Localizações disponíveis
        locations = WeatherDataService.get_available_locations()
        logger.info(f"Localizações disponíveis: {len(locations)}")
        
        for loc in locations:
            status = "✓" if loc['has_current_data'] else "✗"
            logger.info(f"  {status} {loc['name']} ({loc['country']})")
        
        logger.info("=== FIM DO STATUS ===")
        
    except Exception as e:
        logger.error(f"Erro ao mostrar status: {e}")


if __name__ == '__main__':
    init_weather_system()
    
    # Mostrar status final
    app = create_app()
    with app.app_context():
        verify_system()
        show_status()
