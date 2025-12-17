from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# =====================================================
# CONFIGURAÇÃO DO BANCO POSTGRES (RENDER)
# =====================================================
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

# =====================================================
# CRIA TABELA AUTOMATICAMENTE
# =====================================================
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
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# =====================================================
# ROTAS HTML
# =====================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def pagina_cadastro():
    return render_template('cadastro.html')

@app.route('/produtos')
def pagina_produtos():
    return render_template('produtos.html')

@app.route('/suporte')
def suporte():
    return render_template('suporte.html')

# =====================================================
# API - LISTAR PRODUTOS
# =====================================================
@app.route('/api/produtos')
def api_produtos():
    search = request.args.get('search', '')

    conn = get_db_connection()
    cur = conn.cursor()

    if search:
        cur.execute(
            "SELECT * FROM produtos WHERE nome ILIKE %s",
            ('%' + search + '%',)
        )
    else:
        cur.execute("SELECT * FROM produtos")

    produtos = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(produtos)

# =====================================================
# API - CADASTRAR PRODUTO
# =====================================================
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.json

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO produtos (nome, categoria, preco, descricao)
            VALUES (%s, %s, %s, %s)
        """, (
            dados.get('nome'),
            dados.get('categoria'),
            dados.get('preco'),
            dados.get('descricao')
        ))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Produto cadastrado com sucesso"}), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# =====================================================
# START
# =====================================================
if __name__ == '__main__':
    init_db()
    app.run()




