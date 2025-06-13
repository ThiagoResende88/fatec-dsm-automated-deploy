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

Existem duas maneiras principais de executar o projeto: localmente com um ambiente Python ou utilizando Docker, que é o método recomendado.

### Pré-requisitos

* Git
* Python 3.9+ e Pip
* Docker e Docker Compose

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
    # No Windows, use: venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o PostgreSQL localmente** e crie um arquivo `.env` na raiz do projeto com as credenciais do seu banco de dados, seguindo o exemplo do `.gitignore`.

5.  **Execute a aplicação Flask:**
    ```bash
    python app.py
    ```
    A aplicação estará disponível em `http://localhost:8218`.

### Executando com Docker Compose para Desenvolvimento (Recomendado)

Este método é ideal para o desenvolvimento local, pois cria um ambiente completo e isolado com a aplicação e o banco de dados.

1.  **Clone o repositório**, caso ainda não o tenha feito.

2.  **Certifique-se de que o Docker e o Docker Compose estão instalados e rodando.**

3.  **Suba os serviços com o `docker-compose.yml`:**
    ```bash
    docker-compose up --build
    ```
    * Este comando usa o arquivo `docker-compose.yml`, que foi projetado para desenvolvimento.
    * `--build`: Garante que a imagem Docker da aplicação seja construída a partir do `Dockerfile`.
    * **Live Reload:** O código da sua máquina é espelhado dentro do container (`volumes: .:/app`). Qualquer alteração no código-fonte será refletida automaticamente na aplicação, sem a necessidade de reconstruir a imagem.
    * O banco de dados PostgreSQL é iniciado e a porta `8219` é exposta para que você possa acessá-lo com uma ferramenta externa (como DBeaver).

4.  **Acesse a aplicação:**
    Abra seu navegador e acesse `http://localhost:8218`.

5.  **Para parar os serviços:**
    Pressione `Ctrl+C` no terminal e depois execute `docker-compose down`.

---

## 🔄 Pipeline de CI/CD

O projeto utiliza GitHub Actions para automação, conforme definido em `.github/workflows/build.yml`. O workflow é acionado em cada `push` para a branch `main`.

A pipeline é dividida em três etapas (jobs) principais:

1.  **Build e Push da Imagem Docker (`build-and-push`)**:
    * Constrói a imagem Docker da aplicação Flask.
    * Envia a imagem construída para um registro central, o Docker Hub, com a tag `thiagoresende/app-flask-fatec:latest`. Isso cria um artefato imutável que será usado nas etapas seguintes.

2.  **Análise de Qualidade com SonarCloud (`sonarcloud-analysis`)**:
    * Este job é executado após o build.
    * Ele analisa o código-fonte em busca de bugs, vulnerabilidades e "code smells" usando o SonarCloud.
    * Funciona como um **Portão de Qualidade (Quality Gate)**: se o código não atender aos critérios mínimos de qualidade, a pipeline falha e o deploy é interrompido.

3.  **Deploy no Servidor Remoto (`deploy-to-server`)**:
    * Este job só é executado se a análise do SonarCloud for aprovada.
    * Ele se conecta ao servidor de produção via SSH.
    * Copia o arquivo `docker-compose.prod.yml` para o servidor. Este arquivo é otimizado para produção.
    * **Executa o deploy**, onde:
        * `docker compose pull`: Baixa a imagem mais recente do Docker Hub (a mesma que foi construída no passo 1).
        * `docker compose up -d`: Inicia a nova versão da aplicação e do banco de dados em modo detached, usando o `docker-compose.prod.yml`. Este arquivo de produção **não expõe a porta do banco de dados** para o exterior e usa a imagem pronta, garantindo mais segurança e consistência.
        * **Verificação**: Ao final, o script executa comandos de diagnóstico (`docker ps`, `docker logs`) para verificar se os containers subiram corretamente.

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
