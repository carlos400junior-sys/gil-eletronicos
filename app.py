from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Função para iniciar o banco de dados
def init_db():
    conn = sqlite3.connect('gil_eletronicos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            descricao TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- ROTAS PARA OS ARQUIVOS HTML ---

@app.route('/')
def index():
    # Isso procura o arquivo 'index.html' dentro da pasta 'templates'
    return render_template('index.html')

@app.route('/cadastro')
def pagina_cadastro():
    # Isso procura o arquivo 'cadastro.html' dentro da pasta 'templates'
    return render_template('cadastro.html')

@app.route('/lista_produtos')
def lista_produtos():
    return render_template('index.html') # Usaremos a index como vitrine

@app.route('/produtos')
def pagina_produtos():
    return render_template('produtos.html')

@app.route('/api/produtos')
def api_produtos():
    search = request.args.get('search', '')
    conn = sqlite3.connect('gil_eletronicos.db')
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
    cursor = conn.cursor()
    
    if search:
        cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM produtos")
        
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(produtos)


# --- ROTA DE API PARA SALVAR NO BANCO ---

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.json
    nome = dados.get('nome')
    categoria = dados.get('categoria')
    preco = dados.get('preco')
    descricao = dados.get('descricao')

    try:
        conn = sqlite3.connect('gil_eletronicos.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (nome, categoria, preco, descricao) 
            VALUES (?, ?, ?, ?)
        ''', (nome, categoria, preco, descricao))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
if __name__ == '__main__':
    init_db()
    app.run()



