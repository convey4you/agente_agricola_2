"""
Funções auxiliares utilitárias
"""
import os
import secrets
from datetime import datetime, timezone, timedelta
from flask import current_app


def generate_secure_filename(filename):
    """Gerar nome de arquivo seguro"""
    import uuid
    from werkzeug.utils import secure_filename
    
    # Obter extensão do arquivo
    _, extension = os.path.splitext(filename)
    
    # Gerar nome único
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    
    return secure_filename(unique_filename)


def allowed_file(filename, allowed_extensions=None):
    """Verificar se o arquivo tem extensão permitida"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def format_currency(value, currency='BRL'):
    """Formatar valor monetário"""
    try:
        if currency == 'BRL':
            return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            return f"{value:,.2f}"
    except (ValueError, TypeError):
        return "R$ 0,00"


def format_date(date_obj, format_type='short'):
    """Formatar data para exibição"""
    if not date_obj:
        return ""
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except ValueError:
            return date_obj
    
    if format_type == 'short':
        return date_obj.strftime('%d/%m/%Y')
    elif format_type == 'long':
        return date_obj.strftime('%d de %B de %Y')
    elif format_type == 'datetime':
        return date_obj.strftime('%d/%m/%Y às %H:%M')
    else:
        return date_obj.strftime(format_type)


def calculate_days_between(start_date, end_date=None):
    """Calcular dias entre duas datas"""
    if end_date is None:
        end_date = datetime.now()
    
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    return (end_date - start_date).days


def truncate_text(text, max_length=100, suffix='...'):
    """Truncar texto mantendo palavras inteiras"""
    if not text or len(text) <= max_length:
        return text
    
    # Encontrar o último espaço antes do limite
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return f"{truncated}{suffix}"


def generate_api_key():
    """Gerar chave de API segura"""
    return secrets.token_urlsafe(32)


def get_file_size(file_path):
    """Obter tamanho do arquivo em bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def format_file_size(size_bytes):
    """Formatar tamanho do arquivo para exibição"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def slugify(text):
    """Converter texto em slug URL-friendly"""
    import re
    import unicodedata
    
    # Remover acentos
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Converter para minúsculas e substituir espaços/caracteres especiais por hífens
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    
    return text


def get_client_ip():
    """Obter IP do cliente"""
    from flask import request
    
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr


def is_safe_url(target):
    """Verificar se URL é segura para redirecionamento"""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def send_notification_email(to_email, subject, body):
    """Enviar email de notificação (placeholder)"""
    # Implementar integração com serviço de email (SendGrid, SES, etc.)
    current_app.logger.info(f"Email enviado para {to_email}: {subject}")
    return True


def log_user_activity(user_id, action, details=None):
    """Registrar atividade do usuário"""
    current_app.logger.info(f"User {user_id} performed action: {action} - {details}")


def get_season_from_date(date_obj=None):
    """Determinar estação do ano baseada na data"""
    if date_obj is None:
        date_obj = datetime.now()
    
    month = date_obj.month
    
    if month in [12, 1, 2]:
        return 'verao'
    elif month in [3, 4, 5]:
        return 'outono'
    elif month in [6, 7, 8]:
        return 'inverno'
    else:
        return 'primavera'
