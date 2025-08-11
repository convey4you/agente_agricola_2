"""
Serviço para gerenciamento do banco de dados
Inclui funcionalidades de reset, backup e migração
"""
import os
import logging
import shutil
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from sqlalchemy import inspect, text
    from flask import current_app
    from app import db
    from app.models import *
    from app.utils.response_helpers import LoggingHelper
except ImportError as e:
    logging.warning(f"Import error in database_manager: {e}")
    # Fallback para quando os módulos não estão disponíveis durante desenvolvimento

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de operações do banco de dados"""
    
    @staticmethod
    def get_database_info() -> Dict[str, Any]:
        """Obter informações sobre o banco de dados atual"""
        try:
            # Detectar tipo de banco
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            if db_url.startswith('sqlite'):
                db_type = 'SQLite'
                db_file = db_url.replace('sqlite:///', '')
                db_size = os.path.getsize(db_file) if os.path.exists(db_file) else 0
            elif db_url.startswith('postgresql'):
                db_type = 'PostgreSQL'
                db_file = 'N/A (Remote Database)'
                db_size = 0  # Não calculamos o tamanho do PostgreSQL remotamente
            else:
                db_type = 'Unknown'
                db_file = 'N/A'
                db_size = 0
            
            # Obter lista de tabelas
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Contar registros por tabela
            table_counts = {}
            total_records = 0
            
            for table in tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    table_counts[table] = count
                    total_records += count
                except Exception as e:
                    logger.warning(f"Erro ao contar registros da tabela {table}: {e}")
                    table_counts[table] = 'Error'
            
            return {
                'success': True,
                'database_type': db_type,
                'database_file': db_file,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / (1024 * 1024), 2) if db_size > 0 else 0,
                'total_tables': len(tables),
                'total_records': total_records,
                'tables': tables,
                'table_counts': table_counts,
                'connection_url': db_url.split('@')[0] + '@***' if '@' in db_url else 'Local SQLite'
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do banco: {e}")
            return {
                'success': False,
                'error': f"Erro ao obter informações do banco: {str(e)}"
            }
    
    @staticmethod
    def create_backup(backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Criar backup do banco de dados (apenas SQLite)"""
        try:
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            if not db_url.startswith('sqlite'):
                return {
                    'success': False,
                    'error': 'Backup automático só suportado para SQLite. Para PostgreSQL, use pg_dump.'
                }
            
            # Nome do backup
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"backup_{timestamp}"
            
            # Caminhos
            db_file = db_url.replace('sqlite:///', '')
            backup_dir = os.path.join(os.path.dirname(db_file), 'backups')
            backup_file = os.path.join(backup_dir, f"{backup_name}.db")
            
            # Criar diretório de backup se não existir
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copiar arquivo do banco
            if os.path.exists(db_file):
                shutil.copy2(db_file, backup_file)
                
                backup_size = os.path.getsize(backup_file)
                
                logger.info(f"Backup criado: {backup_file}")
                
                return {
                    'success': True,
                    'backup_file': backup_file,
                    'backup_name': backup_name,
                    'backup_size_bytes': backup_size,
                    'backup_size_mb': round(backup_size / (1024 * 1024), 2),
                    'created_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Arquivo do banco não encontrado: {db_file}'
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return {
                'success': False,
                'error': f"Erro ao criar backup: {str(e)}"
            }
    
    @staticmethod
    def reset_database(create_backup_before: bool = True) -> Dict[str, Any]:
        """
        Reset completo do banco de dados - DROP ALL + CREATE ALL
        
        Args:
            create_backup_before: Se deve criar backup antes do reset
            
        Returns:
            Dict com resultado da operação
        """
        try:
            db_info = DatabaseManager.get_database_info()
            original_tables = db_info.get('tables', [])
            original_records = db_info.get('total_records', 0)
            
            LoggingHelper.log_user_action(
                'SYSTEM', 
                'DATABASE_RESET_START', 
                f"Iniciando reset. Tabelas: {len(original_tables)}, Registros: {original_records}"
            )
            
            # Criar backup se solicitado
            backup_result = None
            if create_backup_before:
                backup_result = DatabaseManager.create_backup(
                    f"pre_reset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                if not backup_result.get('success'):
                    logger.warning(f"Falha no backup: {backup_result.get('error')}")
            
            # Detectar tipo de banco
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            is_postgresql = db_url.startswith('postgresql')
            is_sqlite = db_url.startswith('sqlite')
            
            logger.info(f"Iniciando reset do banco: {'PostgreSQL' if is_postgresql else 'SQLite'}")
            
            # 1. DROP ALL TABLES
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                logger.info(f"Removendo {len(existing_tables)} tabelas existentes...")
                
                if is_postgresql:
                    # PostgreSQL: Usar CASCADE para evitar problemas de foreign key
                    with db.engine.connect() as conn:
                        trans = conn.begin()
                        try:
                            # Desabilitar foreign key checks temporariamente
                            for table in existing_tables:
                                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                            trans.commit()
                            logger.info("✅ Tabelas PostgreSQL removidas com CASCADE")
                        except Exception as e:
                            trans.rollback()
                            raise e
                            
                elif is_sqlite:
                    # SQLite: Usar metadata reflect + drop_all
                    db.metadata.reflect(bind=db.engine)
                    db.metadata.drop_all(bind=db.engine)
                    logger.info("✅ Tabelas SQLite removidas com drop_all")
                    
                else:
                    # Outros bancos: tentar drop_all genérico
                    db.metadata.reflect(bind=db.engine)
                    db.metadata.drop_all(bind=db.engine)
                    logger.info("✅ Tabelas removidas com drop_all genérico")
            
            # 2. CREATE ALL TABLES
            logger.info("Recriando todas as tabelas...")
            db.create_all()
            
            # 3. Verificar resultado
            db_info_after = DatabaseManager.get_database_info()
            new_tables = db_info_after.get('tables', [])
            
            logger.info(f"✅ Reset concluído. Tabelas criadas: {len(new_tables)}")
            
            # Log de auditoria
            LoggingHelper.log_user_action(
                'SYSTEM',
                'DATABASE_RESET_COMPLETE',
                f"Reset concluído. Antes: {len(original_tables)} tabelas/{original_records} registros. "
                f"Depois: {len(new_tables)} tabelas/0 registros"
            )
            
            result = {
                'success': True,
                'message': 'Banco de dados resetado com sucesso',
                'before': {
                    'tables': len(original_tables),
                    'records': original_records
                },
                'after': {
                    'tables': len(new_tables),
                    'records': 0
                },
                'tables_created': new_tables,
                'database_type': 'PostgreSQL' if is_postgresql else 'SQLite',
                'reset_timestamp': datetime.now().isoformat()
            }
            
            # Incluir informações de backup se foi criado
            if backup_result and backup_result.get('success'):
                result['backup'] = backup_result
            
            return result
            
        except Exception as e:
            logger.error(f"Erro durante reset do banco: {e}")
            LoggingHelper.log_error(f"Erro durante reset do banco: {e}", 'database.reset')
            
            return {
                'success': False,
                'error': f"Erro durante reset do banco: {str(e)}"
            }
    
    @staticmethod
    def validate_database() -> Dict[str, Any]:
        """Validar integridade do banco de dados"""
        try:
            logger.info("Iniciando validação do banco de dados...")
            
            # Obter informações básicas
            db_info = DatabaseManager.get_database_info()
            if not db_info.get('success'):
                return db_info
            
            issues = []
            warnings = []
            
            # 1. Verificar se todas as tabelas esperadas existem
            expected_models = [
                'user', 'farm', 'culture', 'activity', 
                'marketplace_item', 'conversation', 'message',
                'alert', 'alert_rule', 'user_alert_preference'
            ]
            
            existing_tables = db_info.get('tables', [])
            missing_tables = []
            
            for model in expected_models:
                # Verificar variações de nome (plural, etc.)
                if not any(model in table.lower() or table.lower() in model for table in existing_tables):
                    missing_tables.append(model)
            
            if missing_tables:
                issues.append(f"Tabelas ausentes: {missing_tables}")
            
            # 2. Verificar conectividade
            try:
                db.session.execute(text("SELECT 1"))
                db.session.commit()
            except Exception as e:
                issues.append(f"Erro de conectividade: {e}")
            
            # 3. Verificar integridade (apenas SQLite)
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if db_url.startswith('sqlite'):
                try:
                    result = db.session.execute(text("PRAGMA integrity_check"))
                    integrity_result = result.scalar()
                    if integrity_result != 'ok':
                        issues.append(f"Falha na verificação de integridade: {integrity_result}")
                except Exception as e:
                    warnings.append(f"Não foi possível verificar integridade: {e}")
            
            # 4. Estatísticas de saúde
            health_score = 100
            if issues:
                health_score -= len(issues) * 20
            if warnings:
                health_score -= len(warnings) * 5
            
            health_score = max(0, health_score)
            
            status = 'healthy' if health_score >= 80 else 'degraded' if health_score >= 50 else 'unhealthy'
            
            return {
                'success': True,
                'status': status,
                'health_score': health_score,
                'database_info': db_info,
                'issues': issues,
                'warnings': warnings,
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro durante validação: {e}")
            return {
                'success': False,
                'error': f"Erro durante validação: {str(e)}"
            }
    
    @staticmethod
    def sync_schema() -> Dict[str, Any]:
        """
        Sincronizar schema do banco - criar tabelas e campos ausentes sem perder dados
        Esta operação é segura e não remove dados existentes
        """
        try:
            logger.info("Iniciando sincronização do schema do banco de dados")
            
            # Obter informações antes da sincronização
            before_info = DatabaseManager.get_database_info()
            
            # Detectar tipo de banco
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            db_type = 'SQLite' if db_url.startswith('sqlite') else 'PostgreSQL'
            
            # Obter tabelas existentes
            inspector = inspect(db.engine)
            existing_tables = set(inspector.get_table_names())
            
            # Obter tabelas definidas nos modelos
            model_tables = set()
            new_tables = []
            updated_tables = []
            
            # Criar todas as tabelas definidas nos modelos (apenas as ausentes)
            logger.info("Verificando tabelas definidas nos modelos...")
            
            # Usar create_all que só cria tabelas que não existem
            db.create_all()
            
            # Verificar quais tabelas foram criadas
            new_existing_tables = set(inspector.get_table_names())
            created_tables = new_existing_tables - existing_tables
            
            if created_tables:
                new_tables = list(created_tables)
                logger.info(f"Tabelas criadas: {new_tables}")
            
            # Para cada tabela existente, verificar se há campos novos
            for table_name in existing_tables:
                if hasattr(db.Model.metadata.tables, table_name):
                    # Obter colunas existentes
                    existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
                    
                    # Obter colunas definidas no modelo
                    if table_name in db.Model.metadata.tables:
                        model_columns = set(db.Model.metadata.tables[table_name].columns.keys())
                        
                        # Verificar campos ausentes
                        missing_columns = model_columns - existing_columns
                        
                        if missing_columns:
                            updated_tables.append({
                                'table': table_name,
                                'new_columns': list(missing_columns)
                            })
                            
                            # Para SQLite, precisamos de migração manual para adicionar colunas
                            if db_type == 'SQLite':
                                for column_name in missing_columns:
                                    try:
                                        column_obj = db.Model.metadata.tables[table_name].columns[column_name]
                                        column_type = str(column_obj.type)
                                        default_value = ''
                                        
                                        if hasattr(column_obj, 'default') and column_obj.default:
                                            if hasattr(column_obj.default, 'arg'):
                                                default_value = f" DEFAULT '{column_obj.default.arg}'"
                                            else:
                                                default_value = f" DEFAULT NULL"
                                        elif not column_obj.nullable:
                                            # Para campos obrigatórios, adicionar um valor padrão apropriado
                                            if 'VARCHAR' in column_type or 'TEXT' in column_type:
                                                default_value = " DEFAULT ''"
                                            elif 'INTEGER' in column_type or 'FLOAT' in column_type:
                                                default_value = " DEFAULT 0"
                                            elif 'BOOLEAN' in column_type:
                                                default_value = " DEFAULT 0"
                                            else:
                                                default_value = " DEFAULT NULL"
                                        
                                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}{default_value}"
                                        db.session.execute(text(alter_sql))
                                        logger.info(f"Adicionada coluna {column_name} à tabela {table_name}")
                                        
                                    except Exception as col_error:
                                        logger.warning(f"Erro ao adicionar coluna {column_name} em {table_name}: {col_error}")
            
            # Commit das alterações
            db.session.commit()
            
            # Obter informações após a sincronização
            after_info = DatabaseManager.get_database_info()
            
            # Criar relatório de sincronização
            sync_report = {
                'timestamp': datetime.now().isoformat(),
                'database_type': db_type,
                'tables_before': len(before_info.get('tables', [])),
                'tables_after': len(after_info.get('tables', [])),
                'new_tables': new_tables,
                'updated_tables': updated_tables,
                'data_preserved': True,
                'safe_operation': True
            }
            
            logger.info(f"Sincronização do schema concluída: {len(new_tables)} tabelas criadas, {len(updated_tables)} tabelas atualizadas")
            
            return {
                'success': True,
                'message': 'Schema sincronizado com sucesso',
                'report': sync_report,
                'before_info': before_info,
                'after_info': after_info
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro durante sincronização do schema: {e}")
            return {
                'success': False,
                'error': f"Erro durante sincronização: {str(e)}"
            }
