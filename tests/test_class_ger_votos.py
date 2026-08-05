import pytest
from classes.class_lib import Voto, Gerenciador_votos

@pytest.fixture
def ger_vot():
    return Gerenciador_votos()

def test_instancia(ger_vot):
    assert isinstance(ger_vot, Gerenciador_votos)

def test_votar_sucesso(ger_vot):
    voto1 = Voto(1,1,10,10,10,10,10)
    resposta1 = ger_vot.votar(voto1)
    esperado1 = {'voto_inserido': True, 'id_voto': 1}
    voto2 = Voto(2,1,10,10,10,10,10)
    resposta2 = ger_vot.votar(voto2)
    esperado2 = {'voto_inserido': True, 'id_voto': 2}

    assert resposta1 == esperado1
    assert resposta2 == esperado2

def test_votar_erro(ger_vot):
    voto = Voto(1,1,10,10,10,10,10)
    resposta = ger_vot.votar(voto)
    esperado = {'voto_inserido': False, 'mensagem': 'Este jurado já votou neste projeto.', 'id_voto_existente': 1}

    assert resposta == esperado

def test_obter_lista_votos(ger_vot):
    resposta = ger_vot.obter_lista_votos()

    assert isinstance(resposta, list)
    assert all(isinstance(v, Voto) for v in resposta)

def test_exibir_lista_votos(ger_vot):
    resposta = ger_vot.exibir_lista_votos()

    assert isinstance(resposta, list)
    assert all(isinstance(v, dict) for v in resposta)

def test_somar_votos_estrutura(ger_vot):
    resultado = ger_vot.somar_votos_por_projeto()

    assert isinstance(resultado, list)
    assert len(resultado) == 2
    item = resultado[0]
    for chave in ['id_projeto', 'titulo_projeto', 'unidade_escolar', 'categoria',
                  'ct1', 'ct2', 'ct3', 'ct4', 'ct5', 'total_geral']:
        assert chave in item

def test_somar_votos_valores(ger_vot):
    resultado = ger_vot.somar_votos_por_projeto()
    item = resultado[0]

    assert item['ct1'] == 10
    assert item['ct2'] == 10
    assert item['ct3'] == 10
    assert item['ct4'] == 10
    assert item['ct5'] == 10
    assert item['total_geral'] == 50

def test_somar_votos_lista_vazia():
    ger = Gerenciador_votos()
    ger._lista_votos = []

    resultado = ger.somar_votos_por_projeto()
    assert resultado == []