# app/utils/asset_optimization.py
import os
import gzip
import hashlib
from flask import current_app, request, make_response
from functools import wraps
import mimetypes

class AssetOptimizer:
    """Otimizador de assets estáticos"""
    
    def __init__(self, app=None):
        self.app = app
        self.cache_timeout = 31536000  # 1 ano
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar otimizador com a aplicação"""
        self.app = app
        
        # Configurar compressão
        app.config.setdefault('COMPRESS_MIMETYPES', [
            'text/html',
            'text/css',
            'text/xml',
            'application/json',
            'application/javascript',
            'text/javascript',
            'application/xml+rss',
            'application/atom+xml',
            'image/svg+xml'
        ])
        
        # Registrar blueprint para assets otimizados
        from flask import Blueprint
        
        assets_bp = Blueprint('optimized_assets', __name__)
        
        @assets_bp.route('/static/<path:filename>')
        def optimized_static(filename):
            return self.serve_optimized_asset(filename)
        
        app.register_blueprint(assets_bp)
    
    def serve_optimized_asset(self, filename):
        """Servir asset otimizado"""
        static_folder = current_app.static_folder
        file_path = os.path.join(static_folder, filename)
        
        if not os.path.exists(file_path):
            return "File not found", 404
        
        # Verificar se cliente suporta gzip
        accepts_gzip = 'gzip' in request.headers.get('Accept-Encoding', '')
        
        # Gerar ETag baseado no arquivo
        etag = self._generate_etag(file_path)
        
        # Verificar cache do cliente
        if request.headers.get('If-None-Match') == etag:
            return '', 304
        
        # Ler arquivo
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Comprimir se suportado e benéfico
        if accepts_gzip and self._should_compress(filename):
            content = gzip.compress(content)
            encoding = 'gzip'
        else:
            encoding = None
        
        # Criar resposta
        response = make_response(content)
        
        # Headers de cache
        response.headers['ETag'] = etag
        response.headers['Cache-Control'] = f'public, max-age={self.cache_timeout}'
        
        # Content-Type
        mimetype, _ = mimetypes.guess_type(filename)
        if mimetype:
            response.headers['Content-Type'] = mimetype
        
        # Encoding
        if encoding:
            response.headers['Content-Encoding'] = encoding
        
        return response
    
    def _generate_etag(self, file_path):
        """Gerar ETag para arquivo"""
        stat = os.stat(file_path)
        etag_data = f"{stat.st_mtime}-{stat.st_size}"
        return hashlib.md5(etag_data.encode()).hexdigest()
    
    def _should_compress(self, filename):
        """Verificar se arquivo deve ser comprimido"""
        # Não comprimir arquivos já comprimidos
        compressed_extensions = ['.gz', '.zip', '.rar', '.7z', '.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        for ext in compressed_extensions:
            if filename.lower().endswith(ext):
                return False
        
        # Comprimir apenas arquivos de texto
        text_extensions = ['.css', '.js', '.html', '.xml', '.json', '.svg', '.txt']
        
        for ext in text_extensions:
            if filename.lower().endswith(ext):
                return True
        
        return False

def compress_response(f):
    """Decorator para comprimir respostas HTTP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        
        # Verificar se cliente aceita gzip
        accepts_gzip = 'gzip' in request.headers.get('Accept-Encoding', '')
        
        if not accepts_gzip:
            return response
        
        # Verificar se content-type deve ser comprimido
        content_type = response.headers.get('Content-Type', '')
        
        compressible_types = [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'text/xml',
            'application/xml'
        ]
        
        should_compress = any(ct in content_type for ct in compressible_types)
        
        if should_compress and len(response.data) > 1024:  # Só comprimir se > 1KB
            response.data = gzip.compress(response.data)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.data)
        
        return response
    
    return decorated_function

class LazyLoadingHelper:
    """Helper para lazy loading de componentes"""
    
    @staticmethod
    def generate_lazy_image_html(src, alt="", css_class="", placeholder_color="#f0f0f0"):
        """Gerar HTML para imagem com lazy loading"""
        return f'''
        <img 
            data-src="{src}" 
            alt="{alt}" 
            class="lazy-load {css_class}"
            style="background-color: {placeholder_color};"
            loading="lazy"
        />
        '''
    
    @staticmethod
    def generate_lazy_script():
        """Gerar script JavaScript para lazy loading"""
        return '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const lazyImages = document.querySelectorAll('.lazy-load');
            
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy-load');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        });
        </script>
        '''

class CDNHelper:
    """Helper para integração com CDN"""
    
    def __init__(self, cdn_base_url=None):
        self.cdn_base_url = cdn_base_url
        self._config_loaded = False
    
    def _ensure_config_loaded(self):
        """Carregar configuração do CDN se ainda não carregada"""
        if not self._config_loaded:
            try:
                from flask import current_app
                if current_app and not self.cdn_base_url:
                    self.cdn_base_url = current_app.config.get('CDN_BASE_URL')
                self._config_loaded = True
            except RuntimeError:
                # Fora do contexto da aplicação
                self._config_loaded = True
    
    def asset_url(self, filename):
        """Gerar URL do asset via CDN"""
        self._ensure_config_loaded()
        if self.cdn_base_url:
            return f"{self.cdn_base_url.rstrip('/')}/{filename.lstrip('/')}"
        else:
            return f"/static/{filename}"
    
    def image_url(self, filename, width=None, height=None, quality=85):
        """Gerar URL de imagem otimizada via CDN"""
        self._ensure_config_loaded()
        base_url = self.asset_url(filename)
        
        if not self.cdn_base_url:
            return base_url
        
        # Parâmetros de otimização (exemplo para Cloudinary)
        params = []
        
        if width:
            params.append(f"w_{width}")
        
        if height:
            params.append(f"h_{height}")
        
        if quality != 85:
            params.append(f"q_{quality}")
        
        if params:
            param_string = ",".join(params)
            return f"{self.cdn_base_url}/image/upload/{param_string}/{filename}"
        
        return base_url

# Instâncias globais
asset_optimizer = AssetOptimizer()
cdn_helper = CDNHelper()

class PerformanceMonitor:
    """Monitor de performance para respostas HTTP"""
    
    def __init__(self):
        self.slow_request_threshold = 2.0  # 2 segundos
    
    def monitor_request(self, f):
        """Decorator para monitorar performance de requests"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import time
            import logging
            
            start_time = time.time()
            response = f(*args, **kwargs)
            end_time = time.time()
            
            duration = end_time - start_time
            
            if duration > self.slow_request_threshold:
                logging.warning(
                    f"Slow request detected: {duration:.2f}s - {request.endpoint}",
                    extra={
                        'extra_fields': {
                            'request_duration': duration,
                            'request_endpoint': request.endpoint,
                            'request_method': request.method,
                            'request_url': request.url
                        }
                    }
                )
            
            # Adicionar header de performance
            if hasattr(response, 'headers'):
                response.headers['X-Response-Time'] = f"{duration:.3f}s"
            
            return response
        
        return decorated_function

# Instância global do monitor
performance_monitor = PerformanceMonitor()
