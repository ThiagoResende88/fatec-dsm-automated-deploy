from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "automated_deploy")
DB_USER = os.getenv("DB_USER", "thiago")
DB_PASS = os.getenv("DB_PASS", "123")


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None


@app.route("/")
def index():
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados."
    cur = conn.cursor()
    cur.execute("SELECT * FROM tarefas ORDER BY data_criacao DESC;")
    tarefas_raw = cur.fetchall()  # Lista de tuplas
    cur.close()
    conn.close()

    # Convertendo tuplas para dicionários para facilitar o acesso no template (opcional, mas bom)
    tarefas_dict = []
    if tarefas_raw:
        colunas = [desc[0] for desc in cur.description]  # Pega nome das colunas
        for tarefa_tuple in tarefas_raw:
            tarefas_dict.append(dict(zip(colunas, tarefa_tuple)))
    return render_template("index.html", tarefas=tarefas_raw)


# ADICIONAR TAREFAS
@app.route("/add", methods=["POST"])
def add_tarefa():
    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form.get("descricao")  # .get() para campos opcionais

        conn = get_db_connection()
        if not conn:
            return "Erro ao conectar ao banco de dados ao tentar adicionar tarefa."

        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO tarefas (titulo, descricao) VALUES (%s, %s)",
                (titulo, descricao),
            )
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()  # Desfaz em caso de erro
            print(f"Erro ao inserir tarefa: {e}")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("index"))


# EXCLUIR TAREFAS
@app.route("/delete/<int:id>")  # <int:id> captura o ID da URL como um inteiro
def delete_tarefa(id):
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados ao tentar excluir tarefa."

    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM tarefas WHERE id = %s", (id,))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()  # Desfaz em caso de erro
        print(f"Erro ao excluir tarefa: {e}")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("index"))


# ROTA PARA MOSTRAR O FORMULÁRIO DE EDIÇÃO
@app.route("/edit/<int:id>")
def edit_tarefa_form(id):
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados."

    cur = conn.cursor()
    cur.execute("SELECT * FROM tarefas WHERE id = %s", (id,))
    tarefa = cur.fetchone()  # Pega uma única tarefa
    cur.close()
    conn.close()

    if tarefa is None:
        # Se a tarefa não for encontrada, redireciona para a página inicial
        # Poderia também mostrar uma página de erro 404
        return redirect(url_for("index"))

    return render_template("edit.html", tarefa=tarefa)


# EDITE TAREFA
@app.route("/update/<int:id>", methods=["POST"])
def update_tarefa(id):
    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form.get("descricao")
        # Para o checkbox, se ele não for enviado no formulário (desmarcado),
        # request.form['concluida'] daria erro.
        # Então, verificamos se 'concluida' está presente.
        concluida = "concluida" in request.form

        conn = get_db_connection()
        if not conn:
            return "Erro ao conectar ao banco de dados ao tentar atualizar tarefa."

        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE tarefas 
                SET titulo = %s, descricao = %s, concluida = %s 
                WHERE id = %s
            """,
                (titulo, descricao, concluida, id),
            )
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Erro ao atualizar tarefa: {e}")
            # Adicionar tratamento de erro para o usuário
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8218, debug=True)
