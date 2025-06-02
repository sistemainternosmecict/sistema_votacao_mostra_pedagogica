from abc import ABC, abstractmethod

# dados_projeto = {
#     "id_projeto":0,
#     "titulo_projeto":"",
#     "grupo_tematico":0,
#     "unidade_escolar":""
# }

class Projeto_prototype(ABC):
    def __init__(self, dados_projeto:dict):
        self.id_projeto = dados_projeto['id_projeto']
        self.titulo_projeto = dados_projeto['titulo_projeto']
        self.grupo_tematico = dados_projeto['grupo_tematico']
        self.unidade_escolar = dados_projeto['unidade_escolar']

    def obter_projeto(self):
        return {
            "id_projeto":self.id_projeto,
            "titulo_projeto":self.titulo_projeto,
            "grupo_tematico":self.grupo_tematico,
            "unidade_escolar":self.unidade_escolar
        }

class Projeto(Projeto_prototype):
    def __init__(self, dados_projeto:dict) -> None:
        super().__init__(dados_projeto)