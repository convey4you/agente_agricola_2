# Exemplos de Implementação - AuthService

## 🔄 Exemplo 1: Implementação Básica

### 📁 Estrutura de Arquivos
```
my_app/
├── app.py
├── models.py
├── auth_service.py
├── requirements.txt
└── templates/
    ├── login.html
    └── register.html
```

### 📦 requirements.txt
```txt
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Werkzeug==2.3.6
```

### 🗄️ models.py
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    experience_level = db.Column(db.String(20), default='beginner')
    cidade = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    onboarding_completed = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nome_completo': self.nome_completo,
            'experience_level': self.experience_level,
            'onboarding_completed': self.onboarding_completed
        }
```

### 🔐 auth_service.py
```python
from flask_login import login_user, logout_user
from models import User, db
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def authenticate_user(email: str, password: str, remember: bool = False) -> dict:
        """Autentica usuário com email e senha"""
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                logger.warning(f"Usuário não encontrado: {email}")
                return {
                    'success': False,
                    'error': 'Credenciais inválidas',
                    'status_code': 401
                }
            
            if not user.check_password(password):
                logger.warning(f"Senha incorreta para: {email}")
                return {
                    'success': False,
                    'error': 'Credenciais inválidas',
                    'status_code': 401
                }
            
            login_user(user, remember=remember)
            logger.info(f"Login realizado com sucesso: {email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'needs_onboarding': not user.onboarding_completed,
                'message': 'Login realizado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro durante autenticação: {e}")
            return {
                'success': False,
                'error': 'Erro interno durante autenticação',
                'status_code': 500
            }
    
    @staticmethod
    def create_user(email: str, password: str, nome_completo: str = '') -> dict:
        """Cria novo usuário no sistema"""
        try:
            # Verificar se email já existe
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {
                    'success': False,
                    'error': f'Já existe uma conta com o email {email}',
                    'error_code': 'EMAIL_EXISTS',
                    'status_code': 409
                }
            
            # Criar usuário
            user = User(
                email=email,
                nome_completo=nome_completo
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Login automático
            login_user(user)
            
            logger.info(f"Usuário criado com sucesso: {email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'user_id': user.id,
                'message': f'Conta criada com sucesso para {email}!'
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário {email}: {e}")
            db.session.rollback()
            
            error_msg = 'Erro interno do servidor'
            if 'UNIQUE constraint failed' in str(e):
                error_msg = f'Email {email} já está em uso'
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': 500
            }
    
    @staticmethod
    def save_onboarding_step(user: User, step: str, data: dict) -> dict:
        """Salva dados de onboarding"""
        try:
            if step == '1':
                user.experience_level = data.get('experience_level', 'beginner')
            elif step == '2':
                if 'full_name' in data:
                    user.nome_completo = data['full_name']
                if 'phone' in data:
                    user.telefone = data['phone']
            elif step == '3':
                if 'location' in data:
                    user.cidade = data['location']
                user.onboarding_completed = True
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Dados do passo {step} salvos com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar onboarding: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Erro ao salvar dados',
                'status_code': 500
            }
```

### 🏃 app.py
```python
from flask import Flask, request, render_template, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_required, logout_user, current_user
from models import db, User
from auth_service import AuthService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas
@app.route('/')
def index():
    if current_user.is_authenticated:
        return f"Olá, {current_user.nome_completo or current_user.email}!"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    remember = bool(request.form.get('remember'))
    
    result = AuthService.authenticate_user(email, password, remember)
    
    if result['success']:
        if result.get('needs_onboarding'):
            return redirect(url_for('onboarding'))
        return redirect(url_for('index'))
    else:
        flash(result['error'], 'error')
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    nome_completo = request.form.get('nome_completo', '')
    
    result = AuthService.create_user(email, password, nome_completo)
    
    if result['success']:
        return redirect(url_for('onboarding'))
    else:
        flash(result['error'], 'error')
        return render_template('register.html')

@app.route('/onboarding')
@login_required
def onboarding():
    return "Página de onboarding aqui"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# API endpoints
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    result = AuthService.authenticate_user(
        data.get('email'),
        data.get('password'),
        data.get('remember', False)
    )
    return jsonify(result), result.get('status_code', 200)

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    result = AuthService.create_user(
        data.get('email'),
        data.get('password'),
        data.get('nome_completo', '')
    )
    return jsonify(result), result.get('status_code', 200)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### 🎨 templates/login.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="email"], input[type="password"] {
            width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;
        }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: red; margin-bottom: 15px; }
        .link { text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <h2>Login</h2>
    
    {% with messages = get_flashed_messages(category_filter=["error"]) %}
        {% if messages %}
            {% for message in messages %}
                <div class="error">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="POST">
        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        
        <div class="form-group">
            <label for="password">Senha:</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <div class="form-group">
            <label>
                <input type="checkbox" name="remember"> Lembrar de mim
            </label>
        </div>
        
        <button type="submit">Entrar</button>
    </form>
    
    <div class="link">
        <a href="{{ url_for('register') }}">Não tem conta? Registre-se</a>
    </div>
</body>
</html>
```

### 🎨 templates/register.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>Registro</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="email"], input[type="password"] {
            width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;
        }
        button { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: red; margin-bottom: 15px; }
        .link { text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <h2>Criar Conta</h2>
    
    {% with messages = get_flashed_messages(category_filter=["error"]) %}
        {% if messages %}
            {% for message in messages %}
                <div class="error">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="POST">
        <div class="form-group">
            <label for="nome_completo">Nome Completo:</label>
            <input type="text" id="nome_completo" name="nome_completo">
        </div>
        
        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        
        <div class="form-group">
            <label for="password">Senha:</label>
            <input type="password" id="password" name="password" required minlength="8">
        </div>
        
        <button type="submit">Criar Conta</button>
    </form>
    
    <div class="link">
        <a href="{{ url_for('login') }}">Já tem conta? Faça login</a>
    </div>
</body>
</html>
```

---

## 🚀 Exemplo 2: Implementação com FastAPI

### 📦 requirements.txt
```txt
fastapi==0.103.0
uvicorn==0.23.2
sqlalchemy==2.0.19
passlib==1.7.4
python-jose==3.3.0
python-multipart==0.0.6
```

### 🔐 auth_service.py (FastAPI)
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import User
import logging

logger = logging.getLogger(__name__)

# Configurações
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        if not AuthService.verify_password(password, user.password_hash):
            return False
        return user
    
    @staticmethod
    def create_user(db: Session, email: str, password: str, nome_completo: str = ""):
        # Verificar se usuário já existe
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            raise ValueError("Email já cadastrado")
        
        # Criar usuário
        hashed_password = AuthService.get_password_hash(password)
        db_user = User(
            email=email,
            password_hash=hashed_password,
            nome_completo=nome_completo
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
```

### 🏃 main.py (FastAPI)
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth_service import AuthService
from database import get_db
from models import User
import logging

app = FastAPI(title="Auth Service")
security = HTTPBearer()

# Modelos Pydantic
class UserCreate(BaseModel):
    email: str
    password: str
    nome_completo: str = ""

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = AuthService.create_user(
            db=db,
            email=user.email,
            password=user.password,
            nome_completo=user.nome_completo
        )
        return {
            "success": True,
            "user_id": db_user.id,
            "message": "Usuário criado com sucesso"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = AuthService.authenticate_user(
        db, user.email, user.password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": authenticated_user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_users_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {
        "id": user.id,
        "email": user.email,
        "nome_completo": user.nome_completo
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🔧 Exemplo 3: Implementação com Django

### 📁 Estrutura Django
```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py
│   └── urls.py
└── auth_app/
    ├── models.py
    ├── views.py
    ├── serializers.py
    └── services.py
```

### 🗄️ models.py (Django)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=200, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Iniciante'),
            ('intermediate', 'Intermediário'),
            ('advanced', 'Avançado'),
        ],
        default='beginner'
    )
    cidade = models.CharField(max_length=100, blank=True)
    onboarding_completed = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

### 🔐 services.py (Django)
```python
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from .models import User
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def create_user(email: str, password: str, nome_completo: str = '') -> dict:
        try:
            if User.objects.filter(email=email).exists():
                return {
                    'success': False,
                    'error': 'Email já cadastrado',
                    'status_code': 409
                }
            
            user = User.objects.create(
                username=email,  # Django requer username
                email=email,
                password=make_password(password),
                nome_completo=nome_completo
            )
            
            return {
                'success': True,
                'user_id': user.id,
                'message': 'Usuário criado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return {
                'success': False,
                'error': 'Erro interno',
                'status_code': 500
            }
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        try:
            user = authenticate(username=email, password=password)
            
            if not user:
                return {
                    'success': False,
                    'error': 'Credenciais inválidas',
                    'status_code': 401
                }
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nome_completo': user.nome_completo,
                    'onboarding_completed': user.onboarding_completed
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return {
                'success': False,
                'error': 'Erro interno',
                'status_code': 500
            }
```

### 🎮 views.py (Django REST Framework)
```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import login
from .services import AuthService

@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    nome_completo = request.data.get('nome_completo', '')
    
    result = AuthService.create_user(email, password, nome_completo)
    
    return Response(
        result,
        status=result.get('status_code', 200)
    )

@api_view(['POST'])
def authenticate(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    result = AuthService.authenticate_user(email, password)
    
    if result['success']:
        # Fazer login do usuário na sessão Django
        user = User.objects.get(email=email)
        login(request, user)
    
    return Response(
        result,
        status=result.get('status_code', 200)
    )
```

---

## 📱 Exemplo 4: Cliente JavaScript/Frontend

### 🌐 auth-client.js
```javascript
class AuthClient {
    constructor(baseUrl = '/api/auth') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('auth_token');
    }
    
    async register(userData) {
        try {
            const response = await fetch(`${this.baseUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            
            const result = await response.json();
            
            if (result.success && result.token) {
                this.setToken(result.token);
            }
            
            return result;
        } catch (error) {
            return {
                success: false,
                error: 'Erro de conexão'
            };
        }
    }
    
    async login(email, password, remember = false) {
        try {
            const response = await fetch(`${this.baseUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, remember })
            });
            
            const result = await response.json();
            
            if (result.success && result.token) {
                this.setToken(result.token);
            }
            
            return result;
        } catch (error) {
            return {
                success: false,
                error: 'Erro de conexão'
            };
        }
    }
    
    async logout() {
        try {
            await fetch(`${this.baseUrl}/logout`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
        } catch (error) {
            console.error('Erro no logout:', error);
        }
        
        this.clearToken();
    }
    
    async getCurrentUser() {
        if (!this.token) return null;
        
        try {
            const response = await fetch(`${this.baseUrl}/me`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Erro ao obter usuário:', error);
        }
        
        return null;
    }
    
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }
    
    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }
    
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }
    
    isAuthenticated() {
        return !!this.token;
    }
}

// Uso do cliente
const authClient = new AuthClient();

// Exemplo de uso
async function handleLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const result = await authClient.login(email, password);
    
    if (result.success) {
        window.location.href = '/dashboard';
    } else {
        alert(result.error);
    }
}

async function handleRegister() {
    const userData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        nome_completo: document.getElementById('nome_completo').value
    };
    
    const result = await authClient.register(userData);
    
    if (result.success) {
        window.location.href = '/onboarding';
    } else {
        alert(result.error);
    }
}
```

### 🎨 login.html (com JavaScript)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        .container { max-width: 400px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: red; margin-bottom: 15px; }
        .loading { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        
        <div id="error" class="error"></div>
        <div id="loading" class="loading">Carregando...</div>
        
        <form id="loginForm">
            <div class="form-group">
                <input type="email" id="email" placeholder="Email" required>
            </div>
            
            <div class="form-group">
                <input type="password" id="password" placeholder="Senha" required>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="remember"> Lembrar de mim
                </label>
            </div>
            
            <button type="submit">Entrar</button>
        </form>
        
        <p><a href="register.html">Criar conta</a></p>
    </div>
    
    <script src="auth-client.js"></script>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember').checked;
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').textContent = '';
            
            const result = await authClient.login(email, password, remember);
            
            document.getElementById('loading').style.display = 'none';
            
            if (result.success) {
                if (result.needs_onboarding) {
                    window.location.href = 'onboarding.html';
                } else {
                    window.location.href = 'dashboard.html';
                }
            } else {
                document.getElementById('error').textContent = result.error;
            }
        });
    </script>
</body>
</html>
```

---

## 🐳 Exemplo 5: Deployment com Docker

### 📦 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar usuário não-root
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### 🐳 docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/authdb
      - SECRET_KEY=your-very-secret-key
      - FLASK_ENV=production
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=authdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### ⚙️ .env
```env
SECRET_KEY=your-very-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/authdb
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=production
LOG_LEVEL=INFO
```

---

*Este documento contém exemplos práticos de implementação do AuthService em diferentes tecnologias e contextos.*
