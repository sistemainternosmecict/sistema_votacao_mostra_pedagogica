from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Conexão com SQLite
engine = create_engine('sqlite:///jurados.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Modelo da Tabela
class Jurado(Base):
    __tablename__ = 'tb_jurados'

    id_jurado = Column(Integer, primary_key=True, autoincrement=True)
    nome_jurado = Column(String, nullable=False)
    num_unico_jurado = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Jurado(id={self.id_jurado}, nome='{self.nome_jurado}', num_unico='{self.num_unico_jurado}')>"

# Cria a tabela
Base.metadata.create_all(engine)

# Métodos de manipulação
class JuradoRepository:
    def __init__(self):
        self.session = Session()

    def inserir_jurado(self, nome, num_unico):
        novo_jurado = Jurado(nome_jurado=nome, num_unico_jurado=num_unico)
        self.session.add(novo_jurado)
        self.session.commit()
        return novo_jurado

    def atualizar_jurado(self, id_jurado, nome=None, num_unico=None):
        jurado = self.session.query(Jurado).filter_by(id_jurado=id_jurado).first()
        if not jurado:
            return None
        if nome:
            jurado.nome_jurado = nome
        if num_unico:
            jurado.num_unico_jurado = num_unico
        self.session.commit()
        return jurado

    def remover_jurado(self, id_jurado):
        jurado = self.session.query(Jurado).filter_by(id_jurado=id_jurado).first()
        if jurado:
            self.session.delete(jurado)
            self.session.commit()
            return True
        return False

    def listar_jurados(self):
        return self.session.query(Jurado).all()
