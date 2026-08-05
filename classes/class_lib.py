from classes.projetos_lista import projetos
from classes.model_jurado import JuradoRepository
from classes.model_voto import VotoRepository
from abc import ABC, abstractmethod
from datetime import datetime

class Projeto:
    def __init__(self, dados_projeto:dict)->None:
        self.id_projeto:int = dados_projeto['id_projeto']
        self.titulo_projeto:str = dados_projeto['titulo_projeto']
        self.grupo_tematico:int = dados_projeto['grupo_tematico']
        self.unidade_escolar:str = dados_projeto['unidade_escolar']
        self.link_projeto:str = dados_projeto['link_projeto']
        self.categoria:str = dados_projeto['categoria']

    def obter_dados(self)->dict:
        return {
            "id_projeto":self.id_projeto,
            "titulo_projeto":self.titulo_projeto,
            "grupo_tematico":self.grupo_tematico,
            "unidade_escolar":self.unidade_escolar,
            "link_projeto":self.link_projeto,
            "categoria":self.categoria
        }

class Gerenciador_projetos:
    def __init__(self):
        self.projetos:list[Projeto] = []
        self._carregar_lista_projetos(projetos)

    def _carregar_lista_projetos(self, lista_externa:list[dict])->None:
        for projeto in lista_externa:
            self.inserir_projeto_lista(Projeto(projeto))
    
    def inserir_projeto_lista(self, projeto:Projeto)->list[Projeto]:
        self.projetos.append(projeto)
        return self.projetos
    
    def obter_lista_projetos(self)->list[Projeto]:
        return self.projetos
    
    def exibir_lista_projetos(self)->list[dict]:
        list_temp = []
        for projeto in self.projetos:
            list_temp.append(projeto.obter_dados())
        return list_temp
    
    def obter_projeto_por_id(self, id_projeto:int)->Projeto:
        for projeto in self.projetos:
            if projeto.id_projeto == id_projeto:
                return projeto
    
    def exibir_projeto_por_id(self, id_projeto:int)->dict:
        for projeto in self.projetos:
            if projeto.id_projeto == id_projeto:
                return projeto.obter_dados()
            
class Usuario(ABC):
    def __init__(self, dados_usuario:dict)->None:
        super().__init__()
        self.nome_completo = dados_usuario['nome_completo'] if 'nome_completo' in dados_usuario else "Usuário sem nome"

class Jurado(Usuario):

    def __init__(self, dados_usuario:dict) -> None:
        super().__init__(dados_usuario)
        self.id_jurado:int = dados_usuario['id_jurado'] if 'id_jurado' in dados_usuario else 1
        self.qnt_votos:int = dados_usuario['qnt_votos'] if 'qnt_votos' in dados_usuario else 0
        self.ies:str = dados_usuario['ies'] if 'ies' in dados_usuario else ""
        self.jurado_model:JuradoRepository = JuradoRepository()
        self.acesso_root:bool = False
        # self.carregar_dados_jurado()

    def carregar_dados_jurado(self)->None:
        model_data = self.jurado_model.carregar_jurado_por_id(self.id_jurado)
        self.id_jurado = model_data.id_jurado
        self.nome_completo = model_data.nome_jurado
        self.qnt_votos = model_data.qnt_votos

    def registrar_jurado(self)->dict:
        return self.jurado_model.inserir_jurado(nome=self.nome_completo, qnt_votos=self.qnt_votos, id=self.id_jurado)

    def obter_dados_jurado(self)->dict:
        return self.__dict__
    
    def incrementar_voto(self)->dict:
        self.qnt_votos += 1
        resposta = self.jurado_model.atualizar_jurado(self.id_jurado, qnt_votos=self.qnt_votos)
        return resposta

class Admin(Usuario):

    def __init__(self, dados_usuario:dict) -> None:
        super().__init__(dados_usuario)
        self.acesso_root:bool = True
    
    def obter_dados_admin(self)->dict:
        return self.__dict__

class Voto:
    def __init__(self, id_projeto:int, id_jurado:int, nota_projeto_ct1:int, nota_projeto_ct2:int, nota_projeto_ct3:int, nota_projeto_ct4:int, nota_projeto_ct5:int):
        self.id_projeto:int = id_projeto
        self.id_jurado:int = id_jurado
        self.nota_projeto_ct1:int = nota_projeto_ct1
        self.nota_projeto_ct2:int = nota_projeto_ct2
        self.nota_projeto_ct3:int = nota_projeto_ct3
        self.nota_projeto_ct4:int = nota_projeto_ct4
        self.nota_projeto_ct5:int = nota_projeto_ct5
        self.voto_model:VotoRepository = VotoRepository()

    def registrar_voto(self)->dict:
        agora = datetime.now()
        return self.voto_model.inserir_voto(agora, self.id_projeto, self.id_jurado, self.nota_projeto_ct1, self.nota_projeto_ct2, self.nota_projeto_ct3, self.nota_projeto_ct4, self.nota_projeto_ct5)
    
    def obter_dados_voto(self)->dict:
        return self.__dict__
    
    def atualizar_voto(self) -> dict:
        return self.voto_model.atualizar_voto(
            id_projeto=self.id_projeto,
            id_jurado=self.id_jurado,
            nota_ct1=self.nota_projeto_ct1,
            nota_ct2=self.nota_projeto_ct2,
            nota_ct3=self.nota_projeto_ct3,
            nota_ct4=self.nota_projeto_ct4,
            nota_ct5=self.nota_projeto_ct5
        )
    
class Gerenciador_votos:
    def __init__(self):
        self._lista_votos:list[Voto] = []
        self._voto_model:VotoRepository = VotoRepository()
        self._ger_proj:Gerenciador_projetos = Gerenciador_projetos()
        self.carregar_votos_registrados()

    def carregar_votos_registrados(self)->None:
        lista_temp = self._voto_model.listar_votos()
        for voto in lista_temp:
            temp_voto = Voto(voto.id_projeto, voto.id_jurado, voto.nota_ct1, voto.nota_ct2, voto.nota_ct3, voto.nota_ct4, voto.nota_ct5)
            self._lista_votos.append(temp_voto)

    def votar(self, voto:Voto)->dict:
        self._lista_votos.append(voto)
        return voto.registrar_voto()
    
    def obter_lista_votos(self)->list[Voto]:
        return self._lista_votos
    
    def exibir_lista_votos(self)->list[Voto]:
        list_temp = []
        for voto in self._lista_votos:
            list_temp.append(voto.obter_dados_voto())
        return list_temp
    
    def somar_votos_por_projeto(self) -> list[dict]:
        soma_por_projeto = {}

        for voto in self._lista_votos:
            id_proj = voto.id_projeto
            
            if id_proj not in soma_por_projeto:
                soma_por_projeto[id_proj] = {
                    'ct1': 0,
                    'ct2': 0,
                    'ct3': 0,
                    'ct4': 0,
                    'ct5': 0
                }

            soma_por_projeto[id_proj]['ct1'] += voto.nota_projeto_ct1
            soma_por_projeto[id_proj]['ct2'] += voto.nota_projeto_ct2
            soma_por_projeto[id_proj]['ct3'] += voto.nota_projeto_ct3
            soma_por_projeto[id_proj]['ct4'] += voto.nota_projeto_ct4
            soma_por_projeto[id_proj]['ct5'] += voto.nota_projeto_ct5

        resultado = []
        for id_proj, notas in soma_por_projeto.items():
            projeto = self._ger_proj.obter_projeto_por_id(id_proj)
            total_geral = sum(notas.values())
            resultado.append({
                'id_projeto': id_proj,
                'titulo_projeto':projeto.obter_dados()['titulo_projeto'],
                'unidade_escolar':projeto.obter_dados()['unidade_escolar'],
                'categoria':projeto.categoria,
                'ct1': notas['ct1'],
                'ct2': notas['ct2'],
                'ct3': notas['ct3'],
                'ct4': notas['ct4'],
                'ct5': notas['ct5'],
                'total_geral': total_geral
            })

        return resultado

    def ranquear_projetos_por_nota(self) -> dict:
        resultados = self.somar_votos_por_projeto()

        # Filtrar por categoria
        categoria_0 = [proj for proj in resultados if proj['categoria'] == 0]
        categoria_1 = [proj for proj in resultados if proj['categoria'] == 1]

        # Primeiro ordena toda a lista só pelo total geral (decrescente)
        categoria_0 = sorted(categoria_0, key=lambda x: x['total_geral'], reverse=True)
        categoria_1 = sorted(categoria_1, key=lambda x: x['total_geral'], reverse=True)

        # Função de desempate com múltiplos critérios
        def criterio_desempate(proj):
            return (
                proj['total_geral'],
                proj['ct3'],
                proj['ct4'],
                proj['ct2']
            )

        # Aplicar desempate apenas nas 3 primeiras posições
        categoria_0_top3 = sorted(categoria_0[:3], key=criterio_desempate, reverse=True)
        categoria_1_top3 = sorted(categoria_1[:3], key=criterio_desempate, reverse=True)

        # Montar o ranking final (top3 desempatado + resto da lista original)
        ranking_categoria_0 = categoria_0_top3 + categoria_0[3:]
        ranking_categoria_1 = categoria_1_top3 + categoria_1[3:]

        return {
            'categoria_0': ranking_categoria_0,
            'categoria_1': ranking_categoria_1
        }
  
    def atualizar_voto(self, voto: Voto) -> dict:
        return voto.atualizar_voto()
    
    def quantidade_votos_por_projeto(self) -> list[dict]:
        votos_por_projeto = {}

        for voto in self._lista_votos:
            id_proj = voto.id_projeto
            if id_proj not in votos_por_projeto:
                votos_por_projeto[id_proj] = 0
            votos_por_projeto[id_proj] += 1

        resultado = []
        for id_proj in sorted(votos_por_projeto.keys()):
            resultado.append({
                'id_projeto': id_proj,
                'quantidade_votos': votos_por_projeto[id_proj]
            })

        return resultado
    
    def quantidade_votos_por_id_projeto(self, id_projeto: int) -> int:
        return sum(1 for voto in self._lista_votos if voto.id_projeto == id_projeto)
