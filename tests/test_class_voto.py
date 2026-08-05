# tests/test_voto.py
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from classes.class_lib import Voto
from classes.model_voto import VotoRepository


@pytest.fixture
def voto_mockado():
    return Voto(
        id_projeto=1,
        id_jurado=2,
        nota_projeto_ct1=10,
        nota_projeto_ct2=10,
        nota_projeto_ct3=10,
        nota_projeto_ct4=10,
        nota_projeto_ct5=10
    )

def test_obter_dados_voto(voto_mockado):
    dados = voto_mockado.obter_dados_voto()

    assert isinstance(dados, dict)
    assert dados["id_projeto"] == 1
    assert dados["id_jurado"] == 2
    assert dados["nota_projeto_ct1"] == 10
    assert dados["nota_projeto_ct2"] == 10
    assert dados["nota_projeto_ct3"] == 10
    assert dados["nota_projeto_ct4"] == 10
    assert dados["nota_projeto_ct5"] == 10


def test_registrar_voto(voto_mockado):
    res = voto_mockado.registrar_voto()
    esperado = {"voto_inserido": True}
    assert res == esperado

def test_atualizar_voto(voto_mockado):
    voto_mockado.nota_projeto_ct1 = 10

    res = voto_mockado.atualizar_voto()
    esperado = {"voto_atualizado": True, "id_voto": 1}

    assert res == esperado
