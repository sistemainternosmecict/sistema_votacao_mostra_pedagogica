# tests/test_jurado.py

import pytest
from unittest.mock import MagicMock, patch
from classes.class_lib import Jurado


@pytest.fixture
def dados_mock():
    return {
        'id_jurado': 1,
        'qnt_votos': 2,
        'ies': 'UFABC',
        'nome_completo': 'Fulano da Silva'
    }

# def test_registrar_jurado(dados_mock):
#     jurado = Jurado(dados_mock)
#     resultado = jurado.registrar_jurado()
#     assert resultado == {
#             "jurado_inserido": True,
#             "jurado": {
#                 "id_jurado": 1,
#                 "nome_jurado": 'Fulano da Silva',
#                 "qnt_votos": 2
#             }
#         }


def test_carregar_dados_jurado(dados_mock):
    jurado = Jurado(dados_mock)
    assert jurado.id_jurado == 1
    assert jurado.nome_completo == 'Fulano da Silva'
    assert jurado.qnt_votos == 2

# def test_obter_dados_jurado(dados_mock, mock_jurado_model):
#     with patch('classes.model_jurado.JuradoRepository', return_value=mock_jurado_model):
#         jurado = Jurado(dados_mock)
#         dados = jurado.obter_dados_jurado()
#         assert isinstance(dados, dict)
#         assert dados['id_jurado'] == 1
#         assert dados['nome_completo'] == 'Fulano da Silva'
