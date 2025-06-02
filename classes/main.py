from usuario import Jurado, Admin
from projeto import Projeto

projetos = [
    {
        "id_projeto":1,
        "titulo_projeto":"Projeto de testes 1",
        "grupo_tematico":1,
        "unidade_escolar":"E.M. Escola de testes 1"
    },
    {
        "id_projeto":2,
        "titulo_projeto":"Projeto de testes 2",
        "grupo_tematico":4,
        "unidade_escolar":"E.M. Escola de testes 2"
    },
    {
        "id_projeto":3,
        "titulo_projeto":"Projeto de testes 3",
        "grupo_tematico":2,
        "unidade_escolar":"E.M. Escola de testes 3"
    },
]

obj_projetos = []

for projeto in projetos:
    obj_projetos.append(Projeto(projeto))

jur1 = Jurado("thyez")

nome = jur1.votar(obj_projetos[1])