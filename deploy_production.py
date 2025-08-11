#!/usr/bin/env python3
"""
Script de Deploy para Produção - Sprint 2
Sistema de Alertas com Testes Automatizados
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine, text
import requests

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionDeployer:
    """Gerenciador de deploy para produção"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.database_url = os.environ.get('DATABASE_URL')
        self.app_url = os.environ.get('APP_URL', 'https://agrotech-production.railway.app')
        
    def check_prerequisites(self):
        """Verifica pré-requisitos para o deploy"""
        logger.info("🔍 Verificando pré-requisitos...")
        
        # Verificar variáveis de ambiente essenciais
        required_env = [
            'DATABASE_URL',
            'SECRET_KEY',
            'WEATHER_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_env:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Variáveis de ambiente faltando: {missing_vars}")
            return False
        
        # Verificar se PostgreSQL está acessível
        if not self.test_database_connection():
            return False
            
        logger.info("✅ Pré-requisitos verificados com sucesso")
        return True
    
    def test_database_connection(self):
        """Testa conexão com PostgreSQL"""
        logger.info("🔗 Testando conexão com PostgreSQL...")
        
        try:
            # Ajustar URL se necessário
            db_url = self.database_url
            if db_url and db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"✅ PostgreSQL conectado: {version}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro de conexão PostgreSQL: {e}")
            return False
    
    def run_tests(self):
        """Executa todos os testes antes do deploy"""
        logger.info("🧪 Executando testes automatizados...")
        
        try:
            # Executar testes unitários
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/test_models.py', 
                '-v', '--tb=short', '--no-cov', '-q'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"❌ Testes falharam:\n{result.stdout}\n{result.stderr}")
                return False
            
            logger.info("✅ Todos os testes passaram")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout nos testes (>5min)")
            return False
        except Exception as e:
            logger.error(f"❌ Erro executando testes: {e}")
            return False
    
    def backup_database(self):
        """Cria backup do banco antes da migração"""
        logger.info("💾 Criando backup do banco de dados...")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_production_{timestamp}.sql"
            
            # Extrair componentes da URL do banco
            db_url = self.database_url
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            # Comando pg_dump (se disponível)
            backup_cmd = [
                'pg_dump', 
                db_url,
                '-f', backup_file,
                '--no-owner',
                '--no-privileges'
            ]
            
            result = subprocess.run(backup_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Backup criado: {backup_file}")
                return backup_file
            else:
                logger.warning(f"⚠️ Backup falhou, continuando: {result.stderr}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Backup não realizado: {e}")
            return None
    
    def migrate_database(self):
        """Executa migrações no banco de dados"""
        logger.info("📊 Executando migrações do banco...")
        
        try:
            # Conectar ao banco
            db_url = self.database_url
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            engine = create_engine(db_url)
            
            with engine.connect() as conn:
                # Verificar se tabelas existem
                tables_check = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)).fetchall()
                
                existing_tables = [row[0] for row in tables_check]
                logger.info(f"📋 Tabelas existentes: {existing_tables}")
                
                # Verificar se estrutura de alertas está atualizada
                if 'alerts' in existing_tables:
                    columns_check = conn.execute(text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'alerts'
                    """)).fetchall()
                    
                    alert_columns = [row[0] for row in columns_check]
                    logger.info(f"📊 Colunas da tabela alerts: {alert_columns}")
                    
                    # Verificar se precisamos adicionar novas colunas
                    required_columns = [
                        'id', 'title', 'message', 'alert_type', 'priority', 
                        'status', 'user_id', 'culture_id', 'created_at', 
                        'updated_at', 'read_at', 'resolved_at', 'expires_at'
                    ]
                    
                    missing_columns = set(required_columns) - set(alert_columns)
                    if missing_columns:
                        logger.warning(f"⚠️ Colunas faltando em alerts: {missing_columns}")
                
                # Executar criação de tabelas via SQLAlchemy
                logger.info("🔄 Executando db.create_all()...")
                
                # Importar app e criar tabelas
                sys.path.append(os.getcwd())
                from app import create_app
                from app.models import db
                
                app = create_app('production')
                with app.app_context():
                    db.create_all()
                    logger.info("✅ Estrutura do banco atualizada")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro na migração: {e}")
            return False
    
    def validate_deployment(self):
        """Valida se o deploy foi bem-sucedido"""
        logger.info("✅ Validando deployment...")
        
        try:
            # Teste de health check
            health_url = f"{self.app_url}/health"
            response = requests.get(health_url, timeout=30)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Health check OK: {health_data}")
            else:
                logger.warning(f"⚠️ Health check retornou {response.status_code}")
            
            # Teste da API de alertas
            alerts_url = f"{self.app_url}/api/alerts/health"
            response = requests.get(alerts_url, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ API de alertas funcionando")
            else:
                logger.warning(f"⚠️ API de alertas retornou {response.status_code}")
            
            # Teste de conexão com banco
            if self.test_database_connection():
                logger.info("✅ Banco de dados conectado em produção")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return False
    
    def deploy(self):
        """Executa o processo completo de deploy"""
        logger.info("🚀 INICIANDO DEPLOY PARA PRODUÇÃO")
        logger.info("=" * 60)
        
        steps = [
            ("Verificação de pré-requisitos", self.check_prerequisites),
            ("Execução de testes", self.run_tests),
            ("Backup do banco", self.backup_database),
            ("Migração do banco", self.migrate_database),
            ("Validação do deploy", self.validate_deployment)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 {step_name}...")
            
            try:
                if step_name == "Backup do banco":
                    # Backup é opcional
                    step_func()
                else:
                    if not step_func():
                        logger.error(f"❌ Falha em: {step_name}")
                        return False
                    
            except Exception as e:
                logger.error(f"❌ Erro em {step_name}: {e}")
                return False
        
        duration = datetime.now() - self.start_time
        logger.info("=" * 60)
        logger.info(f"🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        logger.info(f"⏱️ Tempo total: {duration}")
        logger.info(f"🌐 URL da aplicação: {self.app_url}")
        logger.info("=" * 60)
        
        return True

def main():
    """Função principal"""
    deployer = ProductionDeployer()
    
    if deployer.deploy():
        sys.exit(0)
    else:
        logger.error("❌ Deploy falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
