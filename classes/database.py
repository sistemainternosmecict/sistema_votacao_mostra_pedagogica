from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import os
import sys
import logging

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def caminho_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return ""

# Configurações otimizadas do pool de conexões para evitar timeout
def create_database_engine(db_name):
    caminho_db = os.path.join(caminho_base(), f"{db_name}.db")
    
    # Configurações otimizadas do pool de conexões
    engine = create_engine(
        f"sqlite:///{caminho_db}",
        echo=False,
        poolclass=QueuePool,
        pool_size=20,  # Aumentar o tamanho do pool
        max_overflow=30,  # Aumentar o overflow
        pool_timeout=60,  # Aumentar o timeout
        pool_recycle=3600,  # Reciclar conexões a cada hora
        pool_pre_ping=True,  # Verificar conexões antes de usar
        connect_args={
            "timeout": 60,  # Timeout de conexão SQLite
            "check_same_thread": False,  # Permitir múltiplas threads
            "isolation_level": None,  # Autocommit para melhor performance
        }
    )
    
    # Configurar eventos para logging
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Modo WAL para melhor concorrência
        cursor.execute("PRAGMA synchronous=NORMAL")  # Sincronização normal para balancear performance e segurança
        cursor.execute("PRAGMA cache_size=10000")  # Cache maior para melhor performance
        cursor.execute("PRAGMA temp_store=MEMORY")  # Armazenar temporários em memória
        cursor.close()
        logger.info(f"Configurações SQLite aplicadas para {db_name}")
    
    logger.info(f"Engine criado para {db_name} com configurações otimizadas")
    return engine

# Engines para cada banco
votos_engine = create_database_engine("votos")
projetos_engine = create_database_engine("projetos")
jurados_engine = create_database_engine("jurados")

# Session factories com configurações otimizadas
VotosSession = sessionmaker(
    bind=votos_engine,
    autoflush=False,  # Desabilitar autoflush para melhor performance
    autocommit=False,  # Manter controle manual de transações
    expire_on_commit=False  # Manter objetos válidos após commit
)

ProjetosSession = sessionmaker(
    bind=projetos_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

JuradosSession = sessionmaker(
    bind=jurados_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# Sessões thread-safe
votos_session_factory = scoped_session(VotosSession)
projetos_session_factory = scoped_session(ProjetosSession)
jurados_session_factory = scoped_session(JuradosSession)

def get_votos_session():
    """Retorna uma nova sessão para votos"""
    session = votos_session_factory()
    logger.debug("Nova sessão de votos criada")
    return session

def get_projetos_session():
    """Retorna uma nova sessão para projetos"""
    session = projetos_session_factory()
    logger.debug("Nova sessão de projetos criada")
    return session

def get_jurados_session():
    """Retorna uma nova sessão para jurados"""
    session = jurados_session_factory()
    logger.debug("Nova sessão de jurados criada")
    return session

def close_all_sessions():
    """Fecha todas as sessões ativas"""
    try:
        votos_session_factory.remove()
        projetos_session_factory.remove()
        jurados_session_factory.remove()
        logger.info("Todas as sessões foram fechadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao fechar sessões: {e}")

def get_engine_stats():
    """Retorna estatísticas dos engines para monitoramento"""
    stats = {
        'votos': {
            'pool_size': votos_engine.pool.size(),
            'checked_in': votos_engine.pool.checkedin(),
            'checked_out': votos_engine.pool.checkedout(),
            'overflow': votos_engine.pool.overflow()
        },
        'projetos': {
            'pool_size': projetos_engine.pool.size(),
            'checked_in': projetos_engine.pool.checkedin(),
            'checked_out': projetos_engine.pool.checkedout(),
            'overflow': projetos_engine.pool.overflow()
        },
        'jurados': {
            'pool_size': jurados_engine.pool.size(),
            'checked_in': jurados_engine.pool.checkedin(),
            'checked_out': jurados_engine.pool.checkedout(),
            'overflow': jurados_engine.pool.overflow()
        }
    }
    return stats