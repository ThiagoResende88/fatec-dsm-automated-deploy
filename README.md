# Projeto de Deploy Automatizado - Aplicação Web com CI/CD

Este projeto foi desenvolvido como parte do Trabalho Prático da disciplina de Integração e Entrega Contínua de Software para o curso de Desenvolvimento de Software Multiplataforma (DSM) da Fatec Franca.

O objetivo principal é desenvolver uma aplicação web completa com persistência de dados, utilizando banco de dados relacional, containerização via Docker, versionamento com Git/GitHub e deploy automatizado por meio de GitHub Actions, incluindo verificação de qualidade de código com SonarQube em um servidor remoto.

## 📝 Sumário

- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Funcionalidades da Aplicação](#funcionalidades-da-aplicação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Executar o Projeto](#como-executar-o-projeto)
  - [Pré-requisitos](#pré-requisitos)
  - [Executando Localmente (sem Docker)](#executando-localmente-sem-docker)
  - [Executando com Docker Compose (Recomendado)](#executando-com-docker-compose-recomendado)
- [Pipeline de CI/CD](#pipeline-de-cicd)
- [Acesso à Aplicação em Produção](#acesso-à-aplicação-em-produção)
- [Autor](#autor)

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python com Flask
- **Banco de Dados:** PostgreSQL
- **Containerização:** Docker e Docker Compose
- **Versionamento:** Git e GitHub
- **CI/CD:** GitHub Actions
- **Qualidade de Código:** SonarQube
- **Servidor de Deploy:** Linux (Ubuntu) em `201.23.3.86`

## ✨ Funcionalidades da Aplicação

A aplicação web consiste em um sistema de gerenciamento de tarefas (To-Do List) com as seguintes funcionalidades:

- **C**reate: Adicionar novas tarefas.
- **R**ead: Listar todas as tarefas e visualizar detalhes.
- **U**pdate: Editar tarefas existentes (título, descrição, status de concluída).
- **D**elete: Remover tarefas.

## 📂 Estrutura do Projeto
```
.
├── .github/
│   └── workflows/
│       └── deploy.yml        # Workflow do GitHub Actions para CI/CD
├── templates/                # Templates HTML para o Flask
│   ├── index.html
│   └── edit.html
├── .env                      # Arquivo para variáveis de ambiente locais (NÃO VERSIONADO)
├── .gitignore
├── app.py                    # Arquivo principal da aplicação Flask
├── Dockerfile                # Define a imagem Docker para a aplicação Flask
├── docker-compose.yml        # Orquestra os containers da aplicação e do banco de dados
├── init.sql                  # Script SQL para inicializar o banco de dados (criação da tabela tarefas)
├── README.md                 # Este arquivo
├── requirements.txt          # Dependências Python do projeto
└── sonar-project.properties  # Configurações para análise do SonarQube
```
## 🚀 Como Executar o Projeto

### Pré-requisitos

- Git
- Python 3.9+ e Pip
- Docker e Docker Compose
- PostgreSQL (apenas para execução local sem Docker)

### Executando Localmente (sem Docker)

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/ThiagoResende88/fatec-dsm-automated-deploy.git](https://github.com/ThiagoResende88/fatec-dsm-automated-deploy.git)
    cd fatec-dsm-automated-deploy
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o PostgreSQL localmente:**
    * Certifique-se de ter o PostgreSQL instalado e rodando.
    * Crie um usuário e um banco de dados conforme as credenciais que serão usadas. Exemplo:
      ```sql
      -- No psql
      CREATE USER thiago WITH PASSWORD '123';
      CREATE DATABASE automated_deploy OWNER thiago;
      GRANT ALL PRIVILEGES ON DATABASE automated_deploy TO thiago;
      ```
    * Crie a tabela `tarefas` no banco `automated_deploy` executando o conteúdo do arquivo `init.sql`.

5.  **Crie um arquivo `.env`** na raiz do projeto com as credenciais do seu banco de dados local:
    ```env
    DB_HOST=localhost
    DB_NAME=automated_deploy
    DB_USER=thiago
    DB_PASS=123
    ```

6.  **Execute a aplicação Flask:**
    ```bash
    python app.py
    ```
    A aplicação estará disponível em `http://localhost:8218`.

### Executando com Docker Compose (Recomendado)

Este método gerencia a aplicação Flask e o banco de dados PostgreSQL em containers Docker.

1.  **Clone o repositório (se ainda não o fez):**
    ```bash
    git clone [https://github.com/ThiagoResende88/fatec-dsm-automated-deploy.git](https://github.com/ThiagoResende88/fatec-dsm-automated-deploy.git)
    cd fatec-dsm-automated-deploy
    ```

2.  **Certifique-se de que o Docker e o Docker Compose estão instalados e rodando.**

3.  **Suba os serviços com Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    * O comando `--build` garante que a imagem da aplicação seja construída (ou reconstruída se houver alterações no `Dockerfile` ou código).
    * Na primeira vez, o container do PostgreSQL será inicializado e o script `init.sql` criará a tabela `tarefas`.
    * As variáveis de ambiente para a conexão com o banco já estão configuradas no `docker-compose.yml` para a comunicação entre containers.

4.  **Acesse a aplicação:**
    Abra seu navegador e acesse `http://localhost:8218`.

5.  **Para parar os serviços:**
    Pressione `Ctrl+C` no terminal onde o `docker-compose up` está rodando, e depois execute:
    ```bash
    docker-compose down
    ```
    Para remover os volumes (e apagar os dados do banco), use `docker-compose down -v`.

## 🔄 Pipeline de CI/CD

O projeto utiliza GitHub Actions para Integração Contínua e Deploy Contínuo. O workflow está definido em `.github/workflows/deploy.yml` e é acionado em pushes para a branch `main`.

As etapas do pipeline (conforme o objetivo do trabalho) são:
1.  **Build da Imagem Docker:** Constrói a imagem da aplicação Flask.
2.  **Push para o Docker Hub:** Envia a imagem construída para o repositório `thiagoresende/app-flask-fatec` no Docker Hub.
3.  **Análise com SonarQube (no servidor remoto):**
    * Conecta-se via SSH ao servidor `201.23.3.86`.
    * Inicia um container SonarQube temporariamente.
    * Executa o SonarScanner para analisar o código.
    * Verifica o Quality Gate. Se reprovado, o pipeline falha.
    * Para e remove o container SonarQube.
4.  **Deploy no Servidor Remoto (se SonarQube aprovar):**
    * (A ser implementado) Implanta a aplicação (usando a imagem do Docker Hub) no servidor `201.23.3.86`.

## 🌐 Acesso à Aplicação em Produção (Após Deploy)

Após o deploy bem-sucedido pelo pipeline de CI/CD, a aplicação deverá estar acessível no seguinte endereço (conforme requisitos do trabalho):

- **IP:** `201.23.3.86`
- **Porta:** `8218` (dentro do range 8218-8223)
- **URL:** `http://201.23.3.86:8218`

## 👨‍💻 Autor

- **Nome:** Thiago Dias Resende
- **GitHub:** [ThiagoResende88](https://github.com/ThiagoResende88)
- **LinkedIn:** [Thiago Dias Resende](https://www.linkedin.com/in/thiagodiasresende/)

---
*Este README foi gerado com o auxílio do Gemini.*
