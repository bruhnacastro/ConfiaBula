from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.secret_key = "segredo_simples"  # chave para sessão

CORS(app)

# Função para conectar ao banco
def get_db():
    conn = sqlite3.connect("bulas.db")
    conn.row_factory = sqlite3.Row
    return conn

# Página inicial: lista de medicamentos
@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM medicamentos LIMIT 4")
    medicamentos = cursor.fetchall()

    conn.close()

    return render_template("index.html", medicamentos=medicamentos)

# Favoritar medicamento
@app.route("/favoritar/<int:med_id>")
def favoritar(med_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario_id = session["usuario_id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO favoritos (usuario_id, medicamento_id) VALUES (?, ?)", (usuario_id, med_id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# Página de favoritos
@app.route("/favoritos")
def favoritos():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario_id = session["usuario_id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.nome, m.laboratorio, m.indicacao, m.bula_pdf, m.resumo
        FROM medicamentos m
        JOIN favoritos f ON m.id = f.medicamento_id
        WHERE f.usuario_id = ?
    """, (usuario_id,))
    meds_favoritos = cursor.fetchall()
    conn.close()
    return render_template("favoritos.html", medicamentos=meds_favoritos)

@app.route("/api/medicamentos")
def api_medicamentos():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM medicamentos")
    dados = cursor.fetchall()

    lista = [dict(row) for row in dados]

    conn.close()
    return jsonify(lista)

@app.route("/api/medicamento/<nome>")
def api_buscar(nome):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM medicamentos WHERE LOWER(nome) = LOWER(?)", (nome,))
    dado = cursor.fetchone()

    conn.close()

    if dado:
        return jsonify(dict(dado))
    else:
        return jsonify(None)

@app.route("/api/favoritar", methods=["POST"])
def api_favoritar():
    data = request.get_json()

    usuario_id = data["usuario_id"]
    medicamento_id = data["medicamento_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO favoritos (usuario_id, medicamento_id)
        VALUES (?, ?)
    """, (usuario_id, medicamento_id))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/api/favoritos/<int:usuario_id>")
def api_favoritos(usuario_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.*
        FROM medicamentos m
        JOIN favoritos f ON m.id = f.medicamento_id
        WHERE f.usuario_id = ?
    """, (usuario_id,))

    dados = cursor.fetchall()

    lista = [dict(row) for row in dados]

    conn.close()
    return jsonify(lista)

@app.route("/medicamento/<int:id>")
def detalhe_medicamento(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM medicamentos WHERE id = ?", (id,))
    medicamento = cursor.fetchone()

    conn.close()

    return render_template("detalhe.html", medicamento=medicamento)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        usuario = cursor.fetchone()

        conn.close()

        if usuario:
            session["usuario_id"] = usuario["id"]
            session["nome"] = usuario["nome"]
            return redirect("/")
        else:
            return "Login inválido"

    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db()
        cursor = conn.cursor()

        # 🔍 verifica se já existe
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            conn.close()
            return "⚠️ Esse email já está cadastrado!"

        # 💾 se não existe, cadastra
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        """, (nome, email, senha))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("cadastro.html")

@app.route("/remover_favorito/<int:med_id>")
def remover_favorito(med_id):
    if "usuario_id" not in session:
        return redirect("/login")

    usuario_id = session["usuario_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM favoritos
        WHERE usuario_id = ? AND medicamento_id = ?
    """, (usuario_id, med_id))

    conn.commit()
    conn.close()


    return redirect("/favoritos")

@app.route("/buscar")
def buscar():
    nome = request.args.get("nome")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM medicamentos
        WHERE LOWER(nome) LIKE LOWER(?)
    """, ('%' + nome + '%',))

    resultado = cursor.fetchone()

    conn.close()

    if resultado:
        return redirect(url_for('detalhe_medicamento', id=resultado["id"]))
    else:
        return "Medicamento não encontrado 😢"


if __name__ == "__main__":
    app.run(debug=True)