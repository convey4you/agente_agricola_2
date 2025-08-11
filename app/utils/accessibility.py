"""
Sistema de Acessibilidade para AgroTech Portugal
Implementa recursos de acessibilidade conforme WCAG 2.1
"""

from flask import current_app, request, session
from typing import Dict, Any, List, Optional
import json

class AccessibilityManager:
    """Gerenciador de acessibilidade"""
    
    def __init__(self):
        self.wcag_compliance_level = 'AA'  # WCAG 2.1 Level AA
        self.default_settings = self.get_default_accessibility_settings()
    
    def get_default_accessibility_settings(self) -> Dict[str, Any]:
        """Configurações padrão de acessibilidade"""
        return {
            # Configurações visuais
            'high_contrast': False,
            'large_text': False,
            'font_size_multiplier': 1.0,
            'line_height_multiplier': 1.0,
            'letter_spacing_multiplier': 1.0,
            
            # Configurações de movimento
            'reduced_motion': False,
            'auto_play_videos': True,
            'animations_enabled': True,
            'parallax_effects': True,
            
            # Configurações de navegação
            'keyboard_navigation': True,
            'focus_indicators': True,
            'skip_links': True,
            'breadcrumbs': True,
            
            # Configurações de conteúdo
            'alt_text_enabled': True,
            'captions_enabled': False,
            'audio_descriptions': False,
            'simplified_language': False,
            
            # Configurações de interação
            'click_timeout': 5000,  # ms
            'hover_timeout': 1000,  # ms
            'double_click_prevention': True,
            'error_prevention': True,
            
            # Tecnologias assistivas
            'screen_reader_optimized': False,
            'voice_control_support': False,
            'eye_tracking_support': False,
            
            # Configurações de cor
            'color_blind_friendly': False,
            'color_blind_type': None,  # deuteranopia, protanopia, tritanopia
            'custom_color_palette': None
        }
    
    def get_user_accessibility_settings(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Obter configurações de acessibilidade do usuário"""
        if user_id:
            # Buscar do banco de dados ou cache
            # Por enquanto, usar configurações da sessão
            return session.get('accessibility_settings', self.default_settings)
        
        # Detectar automaticamente algumas preferências do browser
        settings = self.default_settings.copy()
        
        # Detectar preferência por movimento reduzido
        if request and hasattr(request, 'headers'):
            user_agent = request.headers.get('User-Agent', '')
            if 'prefers-reduced-motion' in user_agent:
                settings['reduced_motion'] = True
        
        return settings
    
    def apply_accessibility_styles(self, settings: Dict[str, Any]) -> str:
        """Gerar CSS personalizado para acessibilidade"""
        css_rules = []
        
        # Alto contraste
        if settings.get('high_contrast'):
            css_rules.append("""
                :root {
                    --bg-color: #000000 !important;
                    --text-color: #ffffff !important;
                    --primary-color: #ffff00 !important;
                    --secondary-color: #00ffff !important;
                    --border-color: #ffffff !important;
                    --link-color: #ffff00 !important;
                    --link-hover-color: #00ffff !important;
                }
                
                * {
                    background-color: var(--bg-color) !important;
                    color: var(--text-color) !important;
                    border-color: var(--border-color) !important;
                }
                
                a, button {
                    color: var(--link-color) !important;
                    text-decoration: underline !important;
                }
                
                a:hover, button:hover {
                    color: var(--link-hover-color) !important;
                    background-color: var(--text-color) !important;
                }
            """)
        
        # Texto grande
        if settings.get('large_text'):
            multiplier = settings.get('font_size_multiplier', 1.5)
            css_rules.append(f"""
                :root {{
                    --font-size-base: {16 * multiplier}px;
                }}
                
                * {{
                    font-size: calc(var(--font-size-base) * 1) !important;
                }}
                
                h1 {{ font-size: calc(var(--font-size-base) * 2) !important; }}
                h2 {{ font-size: calc(var(--font-size-base) * 1.75) !important; }}
                h3 {{ font-size: calc(var(--font-size-base) * 1.5) !important; }}
                h4 {{ font-size: calc(var(--font-size-base) * 1.25) !important; }}
                h5 {{ font-size: calc(var(--font-size-base) * 1.125) !important; }}
                h6 {{ font-size: calc(var(--font-size-base) * 1) !important; }}
            """)
        
        # Movimento reduzido
        if settings.get('reduced_motion'):
            css_rules.append("""
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
                
                .parallax {
                    transform: none !important;
                }
                
                video {
                    autoplay: false !important;
                }
            """)
        
        # Indicadores de foco melhorados
        if settings.get('focus_indicators'):
            css_rules.append("""
                *:focus {
                    outline: 3px solid #005fcc !important;
                    outline-offset: 2px !important;
                    box-shadow: 0 0 0 5px rgba(0, 95, 204, 0.3) !important;
                }
                
                a:focus, button:focus, input:focus, select:focus, textarea:focus {
                    background-color: #fff3cd !important;
                    border: 2px solid #005fcc !important;
                }
            """)
        
        # Espaçamento de linha melhorado
        line_height = settings.get('line_height_multiplier', 1.0)
        if line_height > 1.0:
            css_rules.append(f"""
                p, li, td, th {{
                    line-height: {1.5 * line_height} !important;
                }}
            """)
        
        # Espaçamento de letras
        letter_spacing = settings.get('letter_spacing_multiplier', 1.0)
        if letter_spacing > 1.0:
            css_rules.append(f"""
                * {{
                    letter-spacing: {0.05 * letter_spacing}em !important;
                }}
            """)
        
        # Paleta de cores para daltonismo
        if settings.get('color_blind_friendly'):
            color_blind_type = settings.get('color_blind_type', 'deuteranopia')
            
            if color_blind_type == 'deuteranopia':
                css_rules.append("""
                    :root {
                        --success-color: #0066cc !important;
                        --warning-color: #ff6600 !important;
                        --danger-color: #cc0000 !important;
                        --info-color: #6600cc !important;
                        --primary-color: #003366 !important;
                    }
                """)
            elif color_blind_type == 'protanopia':
                css_rules.append("""
                    :root {
                        --success-color: #0088cc !important;
                        --warning-color: #ffaa00 !important;
                        --danger-color: #aa0000 !important;
                        --info-color: #4400aa !important;
                        --primary-color: #002244 !important;
                    }
                """)
            elif color_blind_type == 'tritanopia':
                css_rules.append("""
                    :root {
                        --success-color: #00aa44 !important;
                        --warning-color: #cc4400 !important;
                        --danger-color: #880000 !important;
                        --info-color: #2200aa !important;
                        --primary-color: #004422 !important;
                    }
                """)
        
        return '\n'.join(css_rules)
    
    def generate_skip_links(self) -> str:
        """Gerar links de salto para navegação"""
        return """
        <div class="skip-links" style="position: absolute; top: -40px; left: 0; background: #000; color: #fff; padding: 8px; z-index: 9999; text-decoration: none;">
            <a href="#main-content" class="skip-link">Saltar para conteúdo principal</a>
            <a href="#navigation" class="skip-link">Saltar para navegação</a>
            <a href="#footer" class="skip-link">Saltar para rodapé</a>
        </div>
        
        <style>
        .skip-links {
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        }
        
        .skip-links:focus-within {
            opacity: 1;
            pointer-events: auto;
            top: 0;
        }
        
        .skip-link {
            display: inline-block;
            margin-right: 1rem;
            padding: 0.5rem 1rem;
            background: #005fcc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        
        .skip-link:focus {
            background: #0066ff;
            outline: 2px solid white;
            outline-offset: 2px;
        }
        </style>
        """
    
    def add_aria_attributes(self, html_content: str) -> str:
        """Adicionar atributos ARIA ao conteúdo HTML"""
        # Esta função seria mais complexa na implementação real
        # Por enquanto, retorna o conteúdo sem modificações
        return html_content
    
    def generate_alt_text(self, image_context: str, image_purpose: str = 'decorative') -> str:
        """Gerar texto alternativo para imagens"""
        alt_text_templates = {
            'chart': 'Gráfico mostrando {context}',
            'photo': 'Fotografia de {context}',
            'icon': 'Ícone representando {context}',
            'logo': 'Logótipo da {context}',
            'decorative': '',
            'map': 'Mapa mostrando {context}',
            'diagram': 'Diagrama ilustrando {context}'
        }
        
        template = alt_text_templates.get(image_purpose, 'Imagem de {context}')
        return template.format(context=image_context)
    
    def validate_contrast_ratio(self, foreground: str, background: str) -> Dict[str, Any]:
        """Validar rácio de contraste entre cores"""
        # Implementação simplificada - na realidade usaria biblioteca de cores
        # Por enquanto retorna dados simulados
        return {
            'ratio': 4.5,  # Simulado
            'aa_compliant': True,
            'aaa_compliant': False,
            'recommendations': []
        }
    
    def get_keyboard_shortcuts(self) -> List[Dict[str, str]]:
        """Obter atalhos de teclado disponíveis"""
        return [
            {'key': 'Alt + H', 'description': 'Ir para página inicial'},
            {'key': 'Alt + M', 'description': 'Abrir menu principal'},
            {'key': 'Alt + S', 'description': 'Ir para pesquisa'},
            {'key': 'Alt + C', 'description': 'Ir para conteúdo principal'},
            {'key': 'Alt + F', 'description': 'Ir para rodapé'},
            {'key': 'Ctrl + /', 'description': 'Mostrar/ocultar atalhos'},
            {'key': 'Esc', 'description': 'Fechar diálogos e menus'},
            {'key': 'Tab', 'description': 'Navegar para próximo elemento'},
            {'key': 'Shift + Tab', 'description': 'Navegar para elemento anterior'},
            {'key': 'Enter/Space', 'description': 'Ativar elemento focado'}
        ]
    
    def check_wcag_compliance(self, page_content: str) -> Dict[str, Any]:
        """Verificar conformidade WCAG 2.1"""
        # Implementação simplificada
        issues = []
        
        # Verificar se há imagens sem alt text
        if '<img' in page_content and 'alt=' not in page_content:
            issues.append({
                'level': 'A',
                'criterion': '1.1.1',
                'description': 'Imagens sem texto alternativo',
                'impact': 'serious'
            })
        
        # Verificar se há headings em ordem
        # Implementação simplificada
        
        return {
            'compliance_level': 'AA' if len(issues) == 0 else 'Partial',
            'issues_found': len(issues),
            'issues': issues,
            'score': max(0, 100 - len(issues) * 10)
        }

# Instância global
accessibility_manager = AccessibilityManager()

def apply_accessibility_features(user_settings: Dict[str, Any]) -> Dict[str, str]:
    """Aplicar recursos de acessibilidade baseados nas configurações do usuário"""
    return {
        'css': accessibility_manager.apply_accessibility_styles(user_settings),
        'skip_links': accessibility_manager.generate_skip_links(),
        'keyboard_shortcuts': accessibility_manager.get_keyboard_shortcuts()
    }
