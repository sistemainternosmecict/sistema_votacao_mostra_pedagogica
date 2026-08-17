from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import secrets, ast, os, threading
from classes.class_lib import Gerenciador_projetos, Gerenciador_votos, Voto, Jurado
from classes.jurados_lista import jurados
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit
from classes.projetos_lista import grupos_tematicos, categorias
from classes.projetos_lista import projetos as lista_projetos
from classes.database import close_all_sessions
import traceback, multiprocessing, subprocess, os, time
import uuid

load_dotenv()

def generate_flask_secret_key(length=24):
    return secrets.token_hex(length)

from classes.model_jurado import JuradoRepository
repo_init = JuradoRepository()
repo_init.resetar_todos_acessos()
BOOT_ID = str(uuid.uuid4())

app = Flask(__name__)
app.secret_key = generate_flask_secret_key()
gerenciador_projetos = Gerenciador_projetos()
gerenciador_votos = Gerenciador_votos()

status = 0

socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode="eventlet",
    logger=True,
    engineio_logger=True
    )

class ServidorThread:
    def __init__(self):
        self._thread = None

    def iniciar(self):
        if self._thread and self._thread.is_alive():
            print("Servidor já está rodando.")
            return
        self._thread = threading.Thread(
            target=lambda: socketio.run(app, debug=False, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000),
            daemon=True
        )
        self._thread.start()
        print("Servidor iniciado.")

    def parar(self):
        import requests
        try:
            r = requests.get("http://localhost:5000/shutdown")
            if r.status_code == 200:
                print("Servidor encerrado com sucesso.")
        except Exception as e:
            print(f"Erro ao encerrar o servidor: {e}")
    
    def get_thread(self):
        return self._thread

    def run_production_server(self):
        workers = multiprocessing.cpu_count() * 2 + 1
        
        cmd = [
            'gunicorn',
            '--bind', '0.0.0.0:5000',  # Usando porta 5000 como no seu exemplo
            '--workers', str(workers),
            '--worker-class', 'eventlet',  # IMPORTANTE: eventlet para SocketIO
            '--timeout', '120',
            '--keepalive', '5',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'main:app'  # Seu arquivo é main.py, então main:app
        ]
        
        print(f"Iniciando servidor SocketIO com {workers} workers...")
        subprocess.run(cmd)
    
    def start_gunicorn_thread(self):
        """Inicia Gunicorn em thread separada"""
        def run_gunicorn():
            workers = min(multiprocessing.cpu_count(), 4)
            
            cmd = [
                'gunicorn',
                '--bind', '0.0.0.0:5000',
                '--workers', str(workers),
                '--worker-class', 'eventlet',
                '--worker-connections', '1000',
                '--timeout', '120',
                '--keep-alive', '5',
                '--max-requests', '0',
                '--access-logfile', '-',
                '--error-logfile', '-',
                'main:socketio'
                ]
            
            print(f"🚀 Iniciando Gunicorn em thread com {workers} workers...")
            self.running = True
            
            try:
                self.process = subprocess.Popen(cmd)
                self.process.wait()  # Aguarda o processo terminar
            except Exception as e:
                print(f"❌ Erro no Gunicorn: {e}")
            finally:
                self.running = False
        
        self._thread = threading.Thread(
            target=run_gunicorn, 
            daemon=True
        )
        self._thread.start()
        
        # Aguardar um pouco para garantir que iniciou
        time.sleep(2)
        print("Servidor iniciado.")
        return self.running

@app.route("/")
def index():
    return render_template("index.html", status=status)

@app.route("/inicio")
def inicio():
    jurados_lista = jurados
    # Import JuradoRepository here temporarily if not imported globally
    from classes.model_jurado import JuradoRepository
    repo = JuradoRepository()
    acessos = {j.nome_jurado: j.acesso for j in repo.listar_jurados()}
    return render_template("nome_jurado.html", jurados=jurados_lista, acessos=acessos, boot_id=BOOT_ID)

@app.route("/registrar_jurado", methods=['POST'])
def registrar_jurado():
    jurado = ast.literal_eval(request.form['nome_jurado'])
    obj_jurado = Jurado(jurado)
    
    # Server-side lock check
    if obj_jurado.jurado_model.verificar_acesso(jurado['nome_completo']) == 1:
        return "<script>alert('Acesso negado: Este jurado já está em uso!'); window.location.href='/inicio';</script>"
        
    dados_jurado = obj_jurado.obter_dados_jurado()
    dados_jurado = obj_jurado.registrar_jurado()
    
    # Mark as accessed
    obj_jurado.jurado_model.marcar_acesso(jurado['nome_completo'])
    
    return redirect(url_for('votar', id_jurado=dados_jurado['jurado']['id_jurado'], jurado_nome=dados_jurado['jurado']['nome_jurado']))

@app.route("/votar")
def votar():
    id_jurado = request.args.get("id_jurado")
    jurado_nome = request.args.get("jurado_nome")
    tam_lista_projetos = len(gerenciador_projetos.obter_lista_projetos())
    
    jurado = Jurado({"id_jurado":id_jurado})
    jurado.carregar_dados_jurado()
    
    if jurado.id_jurado is None:
        return "<script>localStorage.removeItem('locked_jurado_id'); localStorage.removeItem('locked_jurado_nome'); window.location.href='/inicio';</script>"
        
    jurado_dados = jurado.obter_dados_jurado()
    jurado_qnt_votos = jurado_dados['qnt_votos']

    votos = gerenciador_votos.exibir_lista_votos()
    votos_jurado = []
    for voto in votos:
        if voto['id_jurado'] == int(id_jurado):
            id_projeto = int(voto['id_projeto'])
            voto['projeto'] = gerenciador_projetos.exibir_projeto_por_id(id_projeto)
            votos_jurado.append(voto)

    if jurado_qnt_votos < tam_lista_projetos:
        dados_projeto = gerenciador_projetos.obter_projeto_por_id(jurado_qnt_votos + 1).obter_dados()
        link = url_for('static', filename=f"pdfs_projetos/{dados_projeto['link_projeto'].replace(" ", "_").lower()}.pdf")
        
        id_projeto = int(dados_projeto['id_projeto'])
        projeto_titulo = dados_projeto['titulo_projeto']
        unidade_escolar = dados_projeto['unidade_escolar']
        grupo_tematico = grupos_tematicos[dados_projeto['grupo_tematico'] - 1]
        categoria = categorias[dados_projeto['categoria']]
        return render_template("votar.html", id_jurado=id_jurado, id_projeto=id_projeto, jurado_nome=jurado_nome, projeto_titulo=projeto_titulo, votos_jurado=votos_jurado, link_projeto=link, unidade_escolar=unidade_escolar, grupo_tematico=grupo_tematico, categoria=categoria)
    return redirect(url_for("fim"))

@app.route("/projeto/<id_jurado>/<id_projeto>")
def detalhes_projeto(id_jurado, id_projeto):
    gerenciador_votos = Gerenciador_votos()
    dados_projeto = gerenciador_projetos.obter_projeto_por_id(int(id_projeto)).obter_dados()
    link = url_for('static', filename=f"pdfs_projetos/{dados_projeto['link_projeto'].replace(" ", "_").lower()}.pdf")
    dados_projeto["link_projeto"] = link
    votos = gerenciador_votos.exibir_lista_votos()
    id_jurado = int(id_jurado)
    grupo_tematico = grupos_tematicos[dados_projeto['grupo_tematico'] - 1]
    categoria = categorias[dados_projeto['categoria']]
    return render_template("detalhes_projeto.html", projeto=dados_projeto, votos=votos, id_jurado=id_jurado, grupo_tematico=grupo_tematico, categoria=categoria)

@app.route("/registrar_novo_voto", methods=["POST"])
def registrar_novo_voto():
    try:
        id_jurado = int(request.form.get("id_jurado"))
        id_projeto = int(request.form.get("id_projeto"))
        nota_ct1 = int(request.form.get("nota_1"))
        nota_ct2 = int(request.form.get("nota_2"))
        nota_ct3 = int(request.form.get("nota_3"))
        nota_ct4 = int(request.form.get("nota_4"))
        nota_ct5 = int(request.form.get("nota_5"))
        jurado_nome = request.form.get("jurado_nome")

        # votos_projeto = gerenciador_votos.quantidade_votos_por_projeto()

        jurado = Jurado({"id_jurado":id_jurado})
        jurado.carregar_dados_jurado()
        titulo_projeto = next((p['titulo_projeto'] for p in lista_projetos if p['id_projeto'] == int(id_projeto)), "Projeto Desconhecido")
        entrada_log = f"MESA {id_jurado} votou em {titulo_projeto}."
        with open('log_votos.txt', 'a', encoding='utf-8') as f:
            f.write(entrada_log + '\n')
        socketio.emit('novo_voto', {'mensagem': entrada_log, 'id_projeto':int(id_projeto), 'id_jurado':int(id_jurado), 'titulo_projeto':titulo_projeto})

        voto = Voto(id_projeto, id_jurado, nota_ct1, nota_ct2, nota_ct3, nota_ct4, nota_ct5)
        resultado = gerenciador_votos.votar(voto)
        if resultado['voto_inserido']:
            jurado.incrementar_voto()
            return redirect(url_for('votar', id_jurado=id_jurado, jurado_nome=jurado_nome))
        return redirect(url_for('votar', id_jurado=id_jurado, jurado_nome=jurado_nome))
    
    except Exception as e:
        # Log do erro para debug
        print(f"Erro na rota /registrar_novo_voto: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Em caso de erro, tentar fechar todas as sessões e redirecionar
        try:
            close_all_sessions()
        except:
            pass
        
        # Redirecionar para a página de votação com mensagem de erro
        if 'id_jurado' in locals() and 'jurado_nome' in locals():
            return redirect(url_for('votar', id_jurado=id_jurado, jurado_nome=jurado_nome))
        else:
            return redirect(url_for('inicio'))

@app.route("/atualizar", methods=["POST"])
def atualizar_voto():
    id_jurado = int(request.form.get("id_jurado"))
    jurado = Jurado({"id_jurado":id_jurado})
    jurado.carregar_dados_jurado()

    jurado_nome = jurado.obter_dados_jurado()['nome_completo']

    voto = Voto(
        id_projeto=int(request.form.get("id_projeto")),
        id_jurado=id_jurado,
        nota_projeto_ct1=int(request.form.get("voto_ct1")),
        nota_projeto_ct2=int(request.form.get("voto_ct2")),
        nota_projeto_ct3=int(request.form.get("voto_ct3")),
        nota_projeto_ct4=int(request.form.get("voto_ct4")),
        nota_projeto_ct5=int(request.form.get("voto_ct5"))
    )
    ger_votos = Gerenciador_votos()
    ger_votos.atualizar_voto(voto)
    return redirect(url_for('votar', id_jurado=id_jurado, jurado_nome=jurado_nome))

@app.route("/fim")
def fim():
    return render_template("fim.html")

@app.route("/rank")
def rankear_projetos():
    if "admin" in session:
        ger_votos = Gerenciador_votos()
        votos = ger_votos.ranquear_projetos_por_nota()
        return render_template("rank.html", votos=votos)
    return "Acesso nao autorizado!"

@app.route("/admin")
def admin_panel():
    return render_template("admin.html")

@app.route("/db_status")
def database_status():
    """Rota para monitorar o status das conexões do banco de dados"""
    if "admin" in session:
        try:
            from classes.database import get_engine_stats
            stats = get_engine_stats()
            return jsonify({
                "status": "success",
                "database_stats": stats,
                "message": "Estatísticas do banco de dados obtidas com sucesso"
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Erro ao obter estatísticas: {str(e)}"
            }), 500
    return jsonify({"status": "error", "message": "Acesso não autorizado"}), 403

@app.route("/login", methods=["POST"])
def login():
    login = request.form['login']
    senha = request.form['senha']
    if login == os.getenv("ADM_LOGIN") and senha == os.getenv("ADM_PASS"):
        session['admin'] = True
        return redirect(url_for("painel"))
    return redirect(url_for("login"))

@app.route("/painel")
def painel():
    global status
    votos_por_projeto = gerenciador_votos.quantidade_votos_por_projeto()
    print(votos_por_projeto)

    try:
        with open('log_votos.txt', 'r', encoding='utf-8') as f:
            log_arquivo = f.readlines()
        log_arquivo = [linha.strip() for linha in log_arquivo]
    except FileNotFoundError:
        log_arquivo = []
    if "admin" in session:
        return render_template("painel.html", status=status, log=log_arquivo)
    return "Acesso nao autorizado!"

@app.route("/iniciar_votacao")
def iniciar_votacao():
    global status
    status = 1
    mensagem = "Votação iniciada"
    socketio.emit('nova_mensagem', {'msg': mensagem, status: status}, to=None)
    return jsonify({"status":status})

@app.route("/encerrar_votacao")
def encerrar_votacao():
    global status
    if "admin" in session:
        status = 0
        mensagem = "Votação encerrada"
        socketio.emit('nova_mensagem', {'msg': mensagem, status: status}, to=None)
        return redirect(url_for("painel"))
    return "Acesso nao autorizado!"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin_panel"))

@app.route('/shutdown', methods=['GET'])
def shutdown():
    """Rota para encerrar o servidor Flask-SocketIO de forma limpa"""
    try:
        close_all_sessions()
        print("Sessões de banco de dados fechadas com sucesso.")
    except Exception as e:
        print(f"Erro ao fechar sessões: {e}")

    # Encerrar o SocketIO de forma segura
    def stop_server():
        print("Encerrando servidor SocketIO...")
        os._exit(0)      # garante encerramento do processo

    threading.Thread(target=stop_server).start()
    return "Servidor encerrando..."

if __name__ == "__main__":
    try:
        socketio.run(app, debug=False, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000)
    finally:
        close_all_sessions()
