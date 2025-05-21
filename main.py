from flask import Flask, render_template, redirect, url_for, request, session
import random, secrets
from classes.model_jurado import JuradoRepository

def generate_flask_secret_key(length=24):
    return secrets.token_hex(length)

app = Flask(__name__)
app.secret_key = generate_flask_secret_key()
repo = JuradoRepository()

@app.route("/")
def index():
    if 'jurado' in session:
        return redirect(url_for(votar))
    return render_template("index.html")

@app.route("/inicio")
def inicio():
    return render_template("nome_jurado.html")

@app.route("/registrar_jurado", methods=['POST'])
def registrar_jurado():
    id_jurado = random.randint(10000, 99999)
    print(f"Registrando um jurado {id_jurado}")
    session["jurado"] = request.form["nome_jurado"]
    repo.inserir_jurado(session['jurado'], id_jurado)
    return redirect(url_for('votar'))

@app.route("/votar")
def votar():
    projeto = "Projeto de teste 1"
    jurado = session['jurado']
    return render_template("votar.html", projeto=projeto, jurado=jurado)

@app.route("/registrar_novo_voto", methods=['POST'])
def registrar_novo_voto():
    jurado = request.form.get("jurado")
    projeto = request.form.get("projeto")
    nota = request.form.get("nota")
    return f"Voto registrado... o jurado {jurado} aferiu {nota} pontos ao projeto {projeto}."

@app.route("/remover/registro")
def logout():
    session.pop('jurado', None)
    return redirect(url_for("index"))