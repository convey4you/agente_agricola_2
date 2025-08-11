"""
Blueprint para administração do sistema de detecção de bots
"""
from flask import Blueprint, jsonify, request
from app.utils.bot_detection import bot_detector
from app.utils.metrics import metrics
import logging

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/bot-stats')
def bot_stats():
    """Estatísticas de detecção de bots"""
    try:
        stats = bot_detector.get_stats()
        
        # Obter métricas do sistema
        summary = metrics.get_metrics_summary()
        counters = summary.get('counters', {})
        
        bot_metrics = {
            'total_bot_requests': counters.get('bot_requests_total', 0),
            'filtered_requests': counters.get('bot_requests_filtered', 0),
            'crawler_requests': counters.get('bot_requests_crawler', 0),
            'scanner_requests': counters.get('bot_requests_scanner', 0),
            'aggressive_requests': counters.get('bot_requests_aggressive', 0)
        }
        
        return jsonify({
            'status': 'success',
            'detector_stats': stats,
            'metrics': bot_metrics,
            'total_requests': counters.get('total_requests', 0)
        })
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas de bot: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bot-whitelist', methods=['POST'])
def add_to_whitelist():
    """Adicionar IP à whitelist"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400
        
        bot_detector.add_to_whitelist(ip_address)
        logging.info(f"IP {ip_address} adicionado à whitelist")
        
        return jsonify({
            'status': 'success',
            'message': f'IP {ip_address} adicionado à whitelist'
        })
    except Exception as e:
        logging.error(f"Erro ao adicionar IP à whitelist: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bot-unblock', methods=['POST'])
def remove_from_blocklist():
    """Remove IP da blocklist"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400
        
        bot_detector.remove_from_blocklist(ip_address)
        logging.info(f"IP {ip_address} removido da blocklist")
        
        return jsonify({
            'status': 'success',
            'message': f'IP {ip_address} removido da blocklist'
        })
    except Exception as e:
        logging.error(f"Erro ao remover IP da blocklist: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-bot-detection', methods=['POST'])
def test_bot_detection():
    """Testa detecção de bot com parâmetros fornecidos"""
    try:
        data = request.get_json()
        
        result = bot_detector.is_bot_request(
            user_agent=data.get('user_agent'),
            ip_address=data.get('ip_address'),
            request_path=data.get('request_path')
        )
        
        return jsonify({
            'status': 'success',
            'detection_result': result
        })
    except Exception as e:
        logging.error(f"Erro ao testar detecção de bot: {e}")
        return jsonify({'error': str(e)}), 500
