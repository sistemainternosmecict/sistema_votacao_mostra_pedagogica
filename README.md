# Sistema de Votação - Mostra Pedagógica

Este é um sistema web e desktop desenvolvido para gerenciar e contabilizar votos em projetos pedagógicos. Ele permite que jurados avaliem projetos através de critérios específicos, contando também com um painel administrativo para controle da votação, acompanhamento em tempo real e geração de ranking final.

## Principais Funcionalidades
- **Votação:** Avaliação de projetos por jurados através de notas.
- **Painel Administrativo:** Iniciar e encerrar votações.
- **Tempo Real:** Acompanhamento de votos em tempo real via WebSockets.
- **Ranking:** Geração automática do ranking de projetos com base nas notas.
- **Interface Híbrida:** Servidor web (Flask) integrado com uma interface Desktop (PySide6).

## Tecnologias Utilizadas
- **Linguagem:** Python >= 3.13
- **Web & API:** Flask, Flask-SocketIO (Eventlet)
- **Banco de Dados:** SQLAlchemy
- **Interface Desktop:** PySide6

## Como rodar o programa (A partir do Código-Fonte)

   ```bash
   # baixar e instalar dependencias
   uv sync

   #rodar interface grafica
   uv run ui.py
   ```

---

## Fluxo de Operação de Eventos (Exemplo: 2 Dias)

### 1º DIA
- Inicie a votação pelo painel.
- Acompanhe por meio da UI o status da votação.
- Após o término da votação do primeiro dia, abra o terminal e faça o backup dos bancos de dados (votos e jurados). O script abaixo fará o backup e limpará os dados para o dia seguinte:
  ```bash
  ./backup.sh
  ```

### 2º DIA
- Inicie a votação novamente.
- Acompanhe por meio da UI o status da votação.
- Ao final, consulte o ranking no painel de administração.
