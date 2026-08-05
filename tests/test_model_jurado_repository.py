import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from classes.model_jurado import Base, JuradoRepository

@pytest.fixture
def repo():
    engine = create_engine('sqlite:///jurados.db', echo=False)
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    repo = JuradoRepository()
    repo.session = TestingSession()
    return repo

# def test_inserir_jurado(repo):
#     resultado = repo.inserir_jurado(nome="Maria", qnt_votos=5, id=1)
#     assert resultado["jurado_inserido"] is True
#     assert resultado["jurado"]["nome_jurado"] == "Maria"
#     assert resultado["jurado"]["qnt_votos"] == 5

# def test_inserir_jurado_duplicado(repo):
#     repo.inserir_jurado(nome="João", qnt_votos=3, id=2)
#     resultado = repo.inserir_jurado(nome="João", qnt_votos=4, id=3)
#     assert resultado["jurado_inserido"] is False
#     assert resultado["mensagem"] == "Jurado já existe no banco de dados."

# def test_atualizar_jurado(repo):
#     repo.inserir_jurado(nome="Ana", qnt_votos=2, id=4)
#     resposta = repo.atualizar_jurado(id_jurado=4, nome="Ana Clara", qnt_votos=10)
#     assert resposta["jurado_atualizado"] is True
#     jurado = repo.carregar_jurado_por_id(4)
#     assert jurado.nome_jurado == "Ana Clara"
#     assert jurado.qnt_votos == 10

def test_carregar_jurado_por_id(repo):
    jurado = repo.carregar_jurado_por_id(1)
    assert jurado.nome_jurado == "Maria"
    assert jurado.qnt_votos == 5

# def test_remover_jurado(repo):
#     repo.inserir_jurado(nome="Lucas", qnt_votos=0, id=6)
#     resultado = repo.remover_jurado(6)
#     assert resultado is True
#     jurado = repo.carregar_jurado_por_id(6)
#     assert jurado is None

# def test_listar_jurados(repo):
#     repo.inserir_jurado(nome="A", qnt_votos=1, id=7)
#     repo.inserir_jurado(nome="B", qnt_votos=2, id=8)
#     lista = repo.listar_jurados()
#     assert len(lista) == 2
#     nomes = [j.nome_jurado for j in lista]
#     assert "A" in nomes
#     assert "B" in nomes
