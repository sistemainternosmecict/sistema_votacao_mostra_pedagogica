import sys, socket, requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, 
    QLabel, QFrame, QMessageBox, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QPoint, QTimer, QEvent
from PySide6.QtGui import QColor, QBrush, QPixmap, QIcon
from main import ServidorThread
from PySide6.QtCore import QThread, Signal
from classes.class_lib import Gerenciador_votos
from classes.projetos_lista import projetos as projetos_lista
import socketio, time

class SocketThread(QThread):
    voto_recebido = Signal(str, int, int, str)

    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
        self.connected = False

    def run(self):
        @self.sio.event
        def connect():
            print("Conectado ao servidor SocketIO!")
            self.connected = True

        @self.sio.event
        def disconnect():
            print("Desconectado do servidor SocketIO!")
            self.connected = False

        @self.sio.on("novo_voto")
        def handle_novo_voto(data):
            mensagem = data.get("mensagem", "Novo voto recebido")
            id_projeto = data.get("id_projeto")
            id_jurado = data.get("id_jurado")
            titulo_projeto = data.get("titulo_projeto", "Título desconhecido")

            print(f"Recebido na UI: {mensagem} (Projeto: {id_projeto}, Jurado: {id_jurado})")

            if id_projeto is not None and id_jurado is not None:
                self.voto_recebido.emit(mensagem, id_projeto, id_jurado, titulo_projeto)

        # Tentar conectar com retry
        self.connect_with_retry()
        
        if self.connected:
            self.sio.wait()

    def connect_with_retry(self, max_attempts=10, delay=2):
        addresses = ["http://127.0.0.1:5000", "http://localhost:5000", "http://192.168.100.220:5000"]
        
        for attempt in range(max_attempts):
            print(f"Tentativa {attempt + 1}/{max_attempts}")
            
            for addr in addresses:
                try:
                    print(f"Tentando conectar em {addr}")
                    self.sio.connect(addr)
                    print(f"Conectado com sucesso em {addr}")
                    return True
                except Exception as e:
                    print(f"Falha ao conectar em {addr}: {e}")
                    continue
            
            if attempt < max_attempts - 1:
                print(f"Aguardando {delay} segundos antes da próxima tentativa...")
                time.sleep(delay)
        
        print("Não foi possível conectar após todas as tentativas")
        return False

    def stop(self):
        if self.connected:
            self.sio.disconnect()

class Interface(QWidget):
    def __init__(self):
        super().__init__()
        self._gerenciador_votos = Gerenciador_votos()
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.servidor = ServidorThread()
        self.offset = None
        self.init_ui()
        self.carregar_logs_anteriores()
        # self.barra_superior.installEventFilter(self)

        if self.servidor.get_thread() != None:
            self.start_socket()

    def start_socket(self):
        self.socket_thread = SocketThread()
        self.socket_thread.voto_recebido.connect(self.processar_voto)
        self.socket_thread.start()

    # def eventFilter(self, obj, event):
    #     if obj == self.barra_superior:
    #         if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
    #             self.offset = event.globalPosition().toPoint() - self.pos()
    #             return True

    #         elif event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.LeftButton and self.offset:
    #             self.move(event.globalPosition().toPoint() - self.offset)
    #             return True

    #         elif event.type() == QEvent.Type.MouseButtonRelease:
    #             self.offset = None
    #             return True

        # return super().eventFilter(obj, event)

    def init_ui(self):
        self.setGeometry(100, 100, 600, 300)
        self.setWindowTitle("SVMP v1.0")
        self.setWindowIcon(QIcon("./icon.ico"))
        

        # --- Barra superior personalizada ---
        # self.barra_superior = QWidget()
        # self.barra_superior.setFixedHeight(40)
        # self.barra_superior.setStyleSheet("background-color: #ccc; color: black; border-top-left-radius: 15px; border-top-right-radius: 15px;")

        layout_barra = QHBoxLayout()
        layout_barra.setContentsMargins(10, 0, 10, 0)

        # self.label_titulo = QLabel("SVMP v1.0")
        # self.label_titulo.setStyleSheet("color: black; font-weight: bold; border: none;")
        # layout_barra.addWidget(self.label_titulo)
        layout_barra.addStretch()

        self.btn_fechar = QPushButton("✖")
        self.btn_fechar.setFixedSize(24, 24)
        self.btn_fechar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fechar.clicked.connect(self.close)
        layout_barra.addWidget(self.btn_fechar)


        # --- Lado esquerdo: informações e botões ---
        conteudo_esquerdo = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_esquerdo)
        layout_conteudo.setContentsMargins(10, 10, 10, 10)

        # Logo
        base_size = 150
        logo = QLabel()
        pixmap = QPixmap("static/mostra_cor-removebg-preview.png")  # Ajuste o caminho se necessário
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setScaledContents(True)  # Se quiser redimensionar com suavidade
        logo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        logo.setMinimumHeight(base_size)    # Defina um tamanho limite se preferir
        logo.setMinimumWidth(base_size * 2)    # Defina um tamanho limite se preferir
        logo.setMaximumHeight(base_size * 1.2)    # Defina um tamanho limite se preferir
        logo.setMaximumWidth((base_size * 1.5) * 2)    # Defina um tamanho limite se preferir

        layout_conteudo.addWidget(logo)

        self.label_status = QLabel("<span style='color: red; font-weight: bold;'>🟥Servidor de votação DESLIGADO</span>")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_conteudo.addWidget(self.label_status)

        self.label_ip = QLabel("<span style='color: black; font-weight: bold;'>Inicie o servidor para obter o IP</span>")
        self.label_ip.setTextFormat(Qt.TextFormat.RichText)
        self.label_ip.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.label_ip.setOpenExternalLinks(True)
        self.label_ip.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_conteudo.addWidget(self.label_ip)

        btn_ligar = QPushButton("Ligar Servidor")
        btn_ligar.clicked.connect(self.ligar_servidor)
        btn_ligar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_conteudo.addWidget(btn_ligar)

        btn_desligar = QPushButton("Desligar Servidor")
        btn_desligar.clicked.connect(self.desligar_servidor)
        btn_desligar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_conteudo.addWidget(btn_desligar)

        self.btn_fullscreen = QPushButton("Modo tela cheia")
        self.btn_fullscreen.clicked.connect(self.fullscreen)
        self.btn_fullscreen.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_conteudo.addWidget(self.btn_fullscreen)

        btn_creditos = QPushButton("Créditos")
        btn_creditos.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_creditos.clicked.connect(self.mostrar_creditos)
        layout_conteudo.addWidget(btn_creditos)

        # layout_conteudo.addSpacerItem(QSpacerItem(20, 300, QSizePolicy.Minimum, QSizePolicy.Expanding))

        
        layout_conteudo.addStretch()

        # --- Lado direito: logs ---
        # self.result_label = QTextEdit()
        # self.result_label.setReadOnly(True)
        # self.result_label.setMinimumWidth(500)
        # self.result_label.setStyleSheet("background-color: #fff; color: #111; font-family: Consolas;")
        # self.result_label.setText("Aguardando votos...")

        layout_direita = QHBoxLayout()

        # Caixa de logs (QTextEdit)
        self.result_label = QTextEdit()
        self.result_label.setReadOnly(True)
        self.result_label.setStyleSheet("background-color: #fff; color: #111; font-family: Consolas;")
        self.result_label.setMinimumWidth(500)
        layout_direita.addWidget(self.result_label, 2)

        # Tabela de votos (QTableWidget)
        projetos = list(range(1, len(projetos_lista) + 1))
        jurados = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.criar_tabela_votos(projetos, jurados, self._gerenciador_votos)
        layout_direita.addWidget(self.tabela_votos, 3)

        # --- Layout horizontal: lado a lado ---
        layout_lateral = QHBoxLayout()
        layout_lateral.addWidget(conteudo_esquerdo, 1)
        # layout_lateral.addWidget(self.result_label, 2)
        layout_lateral.addLayout(layout_direita, 3)

        # --- Container principal com barra superior e conteúdo ---
        self.container = QFrame(self)
        self.container.setObjectName("JanelaPrincipal")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        # self.container_layout.addWidget(self.barra_superior)
        self.container_layout.addLayout(layout_lateral)

        # --- Layout geral da interface ---
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.addWidget(self.container)
        self.setLayout(layout_principal)

        self.aplicar_estilo()

    def fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_fullscreen.setText("Modo tela cheia")
        else:
            self.showFullScreen()
            self.btn_fullscreen.setText("Modo janela")

    def aplicar_estilo(self):
        estilo = """
            QPushButton {
                background-color: #444;
                color: white;
                padding: 8px;
                border-radius: 6px;
            }

            #JanelaPrincipal {
                background-color: #ccc;
                border-radius: 8px;
                border: 0.5px solid #666;
            }

            QPushButton:hover {
                background-color: #005f99;
            }

            QLabel {
                padding: 10px;
                font-weight: bold;
            }
        """
        self.setStyleSheet(estilo)

        self.btn_fechar.setStyleSheet(
            """
                background-color: #f00; 
                color: #222;
                border-radius: 12px;
        """
        )

    def ligar_servidor(self):
        self.servidor.iniciar()
        self.label_status.setText("<span style='color: green; font-weight: bold;'>✅Servidor de votação LIGADO</span>")

        ip = self.obter_ip_local()
        self.label_ip.setText(
            f'<a href="http://{ip}:5000" style="color: blue; text-decoration: none;">'
            f'Acesso do jurado: <b>http://{ip}:5000</b></a>'
            '<br/>'
            f'<a href="http://{ip}:5000/admin" style="color: salmon; text-decoration: none;">'
            f'Acesso do admin: <b>http://{ip}:5000/admin</b></a>'
        )

        self.start_socket()
        QTimer.singleShot(3000, self.requisitar_inicio_votacao)

    def desligar_servidor(self):
        self.label_status.setText("<span style='color: red; font-weight: bold;'>⏳ desligando ...</span>")
        QTimer.singleShot(1000, self._parar_servidor)

    def _parar_servidor(self):
        self.servidor.parar()
        self.label_status.setText("<span style='color: red; font-weight: bold;'>🟥Servidor de votação DESLIGADO</span>")
        self.label_ip.setText("")

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= self.barra_superior.height():
    #         self.offset = event.globalPosition().toPoint() - self.pos()

    # def mouseMoveEvent(self, event):
    #     if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
    #         self.move(event.globalPosition().toPoint() - self.offset)

    # def mouseReleaseEvent(self, event):
    #     self.offset = None

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= self.barra_superior.height():
    #         self.offset = event.globalPosition().toPoint() - self.pos()
    #         event.accept()

    # def mouseMoveEvent(self, event):
    #     if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
    #         self.move(event.globalPosition().toPoint() - self.offset)
    #         event.accept()

    # def mouseReleaseEvent(self, event):
    #     self.offset = None
    #     event.accept()


    def mostrar_creditos(self):
        QMessageBox.information(
            self,
            "Créditos",
            "Sistema de Votação da Mostra Pedagógica (SVMP) v1.0\n\n"
            "Desenvolvimento de software interno por:\n"
            "👨‍💻 Thyéz de Oliveira Monteiro - Mat. 9506219\n"
            "Secretaria de Educação - Sala 25\n"
            "SMECICT - 2025"
        )

    def obter_ip_local(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def atualiza_voto(self, data):
        self.result_label.append(f"{data}")

    def carregar_logs_anteriores(self):
        try:
            with open("log_votos.txt", "r", encoding="utf-8") as f:
                logs = f.read()
                self.result_label.setText(logs)
        except FileNotFoundError:
            self.result_label.setText("Nenhum log anterior encontrado.")

    def requisitar_inicio_votacao(self):
        try:
            resposta = requests.get("http://localhost:5000/iniciar_votacao", timeout=5)
            if resposta.status_code == 200:
                print("✔ Votação iniciada com sucesso.")
            else:
                print(f"⚠ Falha ao iniciar votação: {resposta.status_code}")
        except Exception as e:
            print(f"❌ Erro ao requisitar início da votação: {e}")

    def criar_tabela_votos(self, projetos, jurados, gerenciador_votos):
        self.projetos = projetos
        self.jurados = jurados
        self.tabela_votos = QTableWidget()
        self.tabela_votos.setRowCount(len(projetos))
        self.tabela_votos.setColumnCount(len(jurados))
        self.tabela_votos.setVerticalHeaderLabels([str(p) for p in projetos])
        self.tabela_votos.setHorizontalHeaderLabels([str(j) for j in jurados])
        self.tabela_votos.setEditTriggers(QTableWidget.NoEditTriggers)

        for i in range(self.tabela_votos.columnCount()):
            self.tabela_votos.setColumnWidth(i, 30)
        for i in range(self.tabela_votos.rowCount()):
            self.tabela_votos.setRowHeight(i, 30)

        for voto in gerenciador_votos.obter_lista_votos():
                self.pintar_celula_voto(voto.id_projeto, voto.id_jurado)

        self.tabela_votos.setStyleSheet("QTableWidget { background-color: #111; color: white; }")
        self.tabela_votos.resizeColumnsToContents()
        self.tabela_votos.setFixedWidth(380)

    def processar_voto(self, mensagem, id_projeto, id_jurado, titulo_projeto):
        self.result_label.append(f"MESA {id_jurado} votou em {titulo_projeto}.")
        self.pintar_celula_voto(id_projeto, id_jurado)

    def pintar_celula_voto(self, id_projeto, id_jurado):
        try:
            row = self.projetos.index(id_projeto)
            col = self.jurados.index(id_jurado)
        except ValueError:
            print(f"[ERRO] Projeto {id_projeto} ou jurado {id_jurado} não encontrados.")
            return

        item = QTableWidgetItem("V")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(QBrush(QColor("white")))
        item.setBackground(QBrush(QColor("green")))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.tabela_votos.setItem(row, col, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = Interface()
    janela.show()
    sys.exit(app.exec())
