from flask import Flask, render_template, request, redirect, url_for
import psycopg2 # Para conectar ao PostgreSQL
import os
from dotenv import load_dotenv # Para carregar variáveis de .env

load_dotenv() # Carrega variáveis do arquivo .env (se existir)

app = Flask(__name__)

# Configurações do Banco de Dados (exemplo, vamos melhorar isso)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "minha_app_db")
DB_USER = os.getenv("DB_USER", "meu_usuario_db")
DB_PASS = os.getenv("DB_PASS", "minha_senha_db")

def get_db_connection():
    """Estabelece conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(host=DB_HOST,
                                database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS)
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('SELECT version();') # Um teste simples de conexão
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return f"Bem-vindo! Conectado ao PostgreSQL versão: {db_version}"
    else:
        return "Erro ao conectar ao banco de dados."

if __name__ == '__main__':
    # Porta: Use uma do seu range 8218-8223
    # Host '0.0.0.0' faz a aplicação ser acessível na sua rede local,
    # o que é útil para testar de outros dispositivos ou quando estiver em Docker.
    app.run(host='0.0.0.0', port=8218, debug=True)
