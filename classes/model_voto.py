from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from .database import get_votos_session, votos_engine
import contextlib

Base = declarative_base()

# Modelo da Tabela
class Voto(Base):
    __tablename__ = 'tb_votos'

    id_voto = Column(Integer, primary_key=True, autoincrement=True)
    registro_voto = Column(String(30))
    id_projeto = Column(Integer, nullable=False)
    id_jurado = Column(Integer, nullable=False)
    nota_ct1 = Column(Integer, nullable=False)
    nota_ct2 = Column(Integer, nullable=False)
    nota_ct3 = Column(Integer, nullable=False)
    nota_ct4 = Column(Integer, nullable=False)
    nota_ct5 = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Voto(id_voto='{self.id_voto}')>"

# Cria a tabela
Base.metadata.create_all(votos_engine)

class VotoRepository:
    def __init__(self):
        pass

    @contextlib.contextmanager
    def get_session(self):
        """Context manager para gerenciar sessões de forma segura"""
        session = get_votos_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def inserir_voto(self, registro_voto: str, id_projeto: int, id_jurado: int, nota_ct1: int, nota_ct2: int, nota_ct3: int, nota_ct4: int, nota_ct5: int):
        with self.get_session() as session:
            voto_existente = session.query(Voto).filter_by(
                id_projeto=id_projeto,
                id_jurado=id_jurado
            ).first()

            if voto_existente:
                return {
                    "voto_inserido": False,
                    "mensagem": "Este jurado já votou neste projeto.",
                    "id_voto_existente": voto_existente.id_voto
                }

            novo_voto = Voto(
                registro_voto=registro_voto,
                id_projeto=id_projeto,
                id_jurado=id_jurado,
                nota_ct1=nota_ct1,
                nota_ct2=nota_ct2,
                nota_ct3=nota_ct3,
                nota_ct4=nota_ct4,
                nota_ct5=nota_ct5
            )

            session.add(novo_voto)
            # Commit é feito automaticamente pelo context manager

            return {
                "voto_inserido": True,
                "id_voto": novo_voto.id_voto
            }

    def listar_votos(self):
        with self.get_session() as session:
            return session.query(Voto).all()
    
    def atualizar_voto(self, id_projeto: int, id_jurado: int, nota_ct1=None, nota_ct2=None, nota_ct3=None, nota_ct4=None, nota_ct5=None):
        with self.get_session() as session:
            voto = session.query(Voto).filter_by(id_projeto=id_projeto, id_jurado=id_jurado).first()

            if not voto:
                return {"voto_atualizado": False, "mensagem": "Voto não encontrado"}

            # Só atualiza as notas que foram fornecidas (não None)
            if nota_ct1 is not None:
                voto.nota_ct1 = nota_ct1
            if nota_ct2 is not None:
                voto.nota_ct2 = nota_ct2
            if nota_ct3 is not None:
                voto.nota_ct3 = nota_ct3
            if nota_ct4 is not None:
                voto.nota_ct4 = nota_ct4
            if nota_ct5 is not None:
                voto.nota_ct5 = nota_ct5

            # Commit é feito automaticamente pelo context manager
            return {"voto_atualizado": True, "id_voto": voto.id_voto}