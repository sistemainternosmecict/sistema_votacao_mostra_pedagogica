from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from .database import get_jurados_session, jurados_engine
import contextlib

Base = declarative_base()

# Modelo da Tabela
class Jurado(Base):
    __tablename__ = 'tb_jurados'

    id = Column(Integer, primary_key=True, nullable=False)
    id_jurado = Column(Integer)
    nome_jurado = Column(String, nullable=False)
    qnt_votos = Column(Integer)

    def __repr__(self):
        return f"<Jurado(id_jurado={self.id_jurado})>"

# Cria a tabela
Base.metadata.create_all(jurados_engine)

# Métodos de manipulação
class JuradoRepository:
    def __init__(self):
        pass

    @contextlib.contextmanager
    def get_session(self):
        """Context manager para gerenciar sessões de forma segura"""
        session = get_jurados_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def inserir_jurado(self, nome:str, qnt_votos:int, id:int):
        with self.get_session() as session:
            jurado_existente = session.query(Jurado).filter_by(nome_jurado=nome).first()

            if jurado_existente:
                return {
                    "jurado_inserido": False,
                    "mensagem": "Jurado já existe no banco de dados.",
                    "jurado": {
                        "id_jurado": jurado_existente.id_jurado,
                        "nome_jurado": jurado_existente.nome_jurado,
                        "qnt_votos": jurado_existente.qnt_votos
                    }
                }

            novo_jurado = Jurado(id_jurado=id, nome_jurado=nome, qnt_votos=qnt_votos)
            session.add(novo_jurado)
            # Commit é feito automaticamente pelo context manager

            return {
                "jurado_inserido": True,
                "jurado": {
                    "id_jurado": novo_jurado.id_jurado,
                    "nome_jurado": novo_jurado.nome_jurado,
                    "qnt_votos": novo_jurado.qnt_votos
                }
            }

    def atualizar_jurado(self, id_jurado:int, nome:str=None, qnt_votos:int=None):
        with self.get_session() as session:
            jurado = session.query(Jurado).filter_by(id_jurado=id_jurado).first()
            if not jurado:
                return None
            if nome:
                jurado.nome_jurado = nome
            if qnt_votos:
                jurado.qnt_votos = qnt_votos
            # Commit é feito automaticamente pelo context manager
            resposta = {"jurado_atualizado":True}
            return resposta
    
    def carregar_jurado_por_id(self, id_jurado:int)->Jurado:
        with self.get_session() as session:
            jurado = session.query(Jurado).filter(Jurado.id_jurado == id_jurado).first()
            return jurado

    def remover_jurado(self, id_jurado):
        with self.get_session() as session:
            jurado = session.query(Jurado).filter_by(id_jurado=id_jurado).first()
            if jurado:
                session.delete(jurado)
                # Commit é feito automaticamente pelo context manager
                return True
            return False

    def listar_jurados(self):
        with self.get_session() as session:
            return session.query(Jurado).all()
