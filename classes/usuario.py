from abc import ABC, abstractmethod
from projeto import Projeto

class Usuario(ABC):

    @abstractmethod
    def obter_nome(self) -> str:
        pass

class Jurado(Usuario):

    def __init__(self, nome:str) -> None:
        self.nome = nome

    def obter_nome(self) -> str:
        return self.nome

    def votar(self, projeto: Projeto) -> None:
        print("Votou em ", projeto.obter_projeto())

class Admin(Usuario):

    def __init__(self, nome:str) -> None:
        self.nome = nome

    def obter_nome(self) -> str:
        return self.nome