from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from .database import get_projetos_session, projetos_engine
import contextlib

Base = declarative_base()

# Modelo da Tabela
class Projeto(Base):
    __tablename__ = 'tb_projetos'

    id_projeto = Column(Integer, primary_key=True, autoincrement=True)
    titulo_projeto = Column(String(200), nullable=False)
    grupo_tematico = Column(Integer, nullable=False)
    unidade_escolar = Column(String(200), nullable=False)
    link_projeto = Column(String(200), nullable=False)

    def __repr__(self):
        return f"<Projeto(id_projeto='{self.id_projeto}')>"

# Cria a tabela
Base.metadata.create_all(projetos_engine)

class ProjetoRepository:
    def __init__(self):
        pass

    @contextlib.contextmanager
    def get_session(self):
        """Context manager para gerenciar sessões de forma segura"""
        session = get_projetos_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def inserir_projeto(self, dados_projeto:dict)->dict:
        with self.get_session() as session:
            novo_jurado = Projeto(id_projeto=dados_projeto['id_projeto'],
                                  titulo_projeto=dados_projeto['titulo_projeto'],
                                  grupo_tematico=dados_projeto['grupo_tematico'],
                                  unidade_escolar=dados_projeto['unidade_escolar'],
                                  link_projeto=dados_projeto['link_projeto'])
            session.add(novo_jurado)
            # Commit é feito automaticamente pelo context manager
            resposta = {"projeto_inserido":True}
            return resposta
    
    def listar_votos(self):
        # Mantida por compatibilidade, mas como este repositório é de Projeto,
        # retornaremos a lista de projetos. Caso não seja usada, considerar remover.
        with self.get_session() as session:
            return session.query(Projeto).all()