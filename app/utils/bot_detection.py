"""
Sistema de detecção e filtro de bots para melhorar métricas de monitoramento.
"""
import re
import logging
from typing import Dict, Set, Optional, Any
from flask import request
from datetime import datetime, timedelta
from collections import defaultdict, deque

class BotDetector:
    """Detector de tráfego de bots"""
    
    # User agents conhecidos de bots
    BOT_USER_AGENTS = {
        'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider',
        'yandexbot', 'facebookexternalhit', 'twitterbot', 'linkedinbot',
        'whatsapp', 'telegrambot', 'discordbot', 'applebot', 'amazonbot',
        'crawler', 'spider', 'scraper', 'bot', 'curl', 'wget', 'python-requests',
        'postman', 'insomnia', 'httpie', 'node-fetch', 'axios'
    }
    
    # Padrões suspeitos de comportamento de bot
    SUSPICIOUS_PATTERNS = [
        r'/admin',
        r'/wp-admin',
        r'\.php$',
        r'\.asp$',
        r'/phpmyadmin',
        r'/xmlrpc\.php',
        r'/wp-login\.php',
        r'/robots\.txt',
        r'/sitemap\.xml',
        r'/favicon\.ico'
    ]
    
    def __init__(self):
        self.request_history = defaultdict(lambda: deque(maxlen=100))
        self.blocked_ips = set()
        self.whitelist_ips = {'127.0.0.1', '::1'}  # IPs sempre permitidos
        
        # Rate limiting para detectar bots agressivos
        self.rate_limits = {
            'requests_per_minute': 60,
            'requests_per_hour': 300,
            'suspicious_requests_per_hour': 10
        }
        
        self.logger = logging.getLogger(__name__)
    
    def is_bot_request(self, 
                      user_agent: Optional[str] = None,
                      ip_address: Optional[str] = None,
                      request_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Determina se uma requisição vem de um bot.
        
        Returns:
            Dict com informações da detecção:
            - is_bot: bool
            - confidence: float (0-1)
            - reasons: List[str]
            - should_exclude_metrics: bool
        """
        if not user_agent and request:
            user_agent = request.headers.get('User-Agent', '')
        
        if not ip_address and request:
            ip_address = self._get_client_ip()
        
        if not request_path and request:
            request_path = request.path
        
        result = {
            'is_bot': False,
            'confidence': 0.0,
            'reasons': [],
            'should_exclude_metrics': False,
            'bot_type': None
        }
        
        # Verificar IP na whitelist
        if ip_address in self.whitelist_ips:
            return result
        
        # Verificar IP bloqueado
        if ip_address in self.blocked_ips:
            result.update({
                'is_bot': True,
                'confidence': 1.0,
                'reasons': ['IP previamente identificado como bot'],
                'should_exclude_metrics': True,
                'bot_type': 'blocked'
            })
            return result
        
        confidence_score = 0.0
        reasons = []
        
        # 1. Análise do User-Agent
        if user_agent:
            ua_lower = user_agent.lower()
            for bot_pattern in self.BOT_USER_AGENTS:
                if bot_pattern in ua_lower:
                    confidence_score += 0.4
                    reasons.append(f'User-agent contém "{bot_pattern}"')
                    result['bot_type'] = 'crawler'
                    break
            
            # User-agents muito genéricos ou suspeitos
            if not user_agent or user_agent == '-':
                confidence_score += 0.3
                reasons.append('User-agent vazio ou genérico')
            elif len(user_agent) < 10:
                confidence_score += 0.2
                reasons.append('User-agent muito curto')
        
        # 2. Análise do caminho da requisição
        if request_path:
            for pattern in self.SUSPICIOUS_PATTERNS:
                if re.search(pattern, request_path, re.IGNORECASE):
                    confidence_score += 0.3
                    reasons.append(f'Caminho suspeito: {request_path}')
                    result['bot_type'] = 'scanner'
                    break
        
        # 3. Análise de rate limiting
        if ip_address:
            rate_analysis = self._analyze_request_rate(ip_address)
            if rate_analysis['is_suspicious']:
                confidence_score += 0.4
                reasons.extend(rate_analysis['reasons'])
                result['bot_type'] = 'aggressive'
        
        # 4. Análise de headers ausentes
        if request:
            missing_headers = self._check_missing_headers()
            if missing_headers:
                confidence_score += 0.2
                reasons.append(f'Headers suspeitos: {missing_headers}')
        
        # Determinar resultado final
        result['confidence'] = min(confidence_score, 1.0)
        result['reasons'] = reasons
        
        if confidence_score >= 0.7:
            result['is_bot'] = True
            result['should_exclude_metrics'] = True
            # Bloquear IP se muito suspeito
            if confidence_score >= 0.9 and ip_address:
                self.blocked_ips.add(ip_address)
        elif confidence_score >= 0.3:
            result['is_bot'] = True
            result['should_exclude_metrics'] = False  # Bot "bom", manter métricas
        
        return result
    
    def _get_client_ip(self) -> str:
        """Obter IP real do cliente considerando proxies"""
        # Verificar headers de proxy
        if request.headers.get('X-Forwarded-For'):
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers['X-Real-IP']
        else:
            return request.remote_addr or 'unknown'
    
    def _analyze_request_rate(self, ip_address: str) -> Dict[str, Any]:
        """Analisa a taxa de requisições de um IP"""
        now = datetime.utcnow()
        history = self.request_history[ip_address]
        
        # Adicionar requisição atual
        history.append(now)
        
        # Contar requisições no último minuto e hora
        one_minute_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)
        
        recent_requests = [req for req in history if req > one_minute_ago]
        hourly_requests = [req for req in history if req > one_hour_ago]
        
        reasons = []
        is_suspicious = False
        
        if len(recent_requests) > self.rate_limits['requests_per_minute']:
            is_suspicious = True
            reasons.append(f'Muitas requisições por minuto: {len(recent_requests)}')
        
        if len(hourly_requests) > self.rate_limits['requests_per_hour']:
            is_suspicious = True
            reasons.append(f'Muitas requisições por hora: {len(hourly_requests)}')
        
        return {
            'is_suspicious': is_suspicious,
            'reasons': reasons,
            'requests_per_minute': len(recent_requests),
            'requests_per_hour': len(hourly_requests)
        }
    
    def _check_missing_headers(self) -> str:
        """Verifica headers ausentes que indicam comportamento de bot"""
        missing = []
        
        # Headers típicos de navegadores
        if not request.headers.get('Accept'):
            missing.append('Accept')
        
        if not request.headers.get('Accept-Language'):
            missing.append('Accept-Language')
        
        if not request.headers.get('Accept-Encoding'):
            missing.append('Accept-Encoding')
        
        return ', '.join(missing)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do detector"""
        return {
            'blocked_ips_count': len(self.blocked_ips),
            'monitored_ips_count': len(self.request_history),
            'whitelist_count': len(self.whitelist_ips)
        }
    
    def add_to_whitelist(self, ip_address: str):
        """Adiciona IP à whitelist"""
        self.whitelist_ips.add(ip_address)
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
    
    def remove_from_blocklist(self, ip_address: str):
        """Remove IP da blocklist"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)

# Instância global
bot_detector = BotDetector()
