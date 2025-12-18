import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não configurada")

def get_db_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco NUMERIC NOT NULL,
            descricao TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# =========================
# ROTAS HTML
# =========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

# =========================
# API - LISTAR PRODUTOS
# =========================
@app.route('/api/produtos')
def api_produtos():
    search = request.args.get('search', '')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if search:
        cur.execute(
            "SELECT * FROM produtos WHERE nome ILIKE %s ORDER BY id DESC",
            ('%' + search + '%',)
        )
    else:
        cur.execute("SELECT * FROM produtos ORDER BY id DESC")

    produtos = cur.fetchall()

    # converte preco para float
    for p in produtos:
        p["preco"] = float(p["preco"])

    cur.close()
    conn.close()
    return jsonify(produtos)

@app.route('/nota-fiscal')
def nota_fiscal():
    return render_template('nota_fiscal.html')


# =========================
# API - CADASTRAR PRODUTO
# =========================
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO produtos (nome, categoria, preco, descricao)
            VALUES (%s, %s, %s, %s)
        """, (
            dados['nome'],
            dados['categoria'],
            dados['preco'],
            dados.get('descricao')
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Produto cadastrado com sucesso"}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# =========================
# START
# =========================
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



