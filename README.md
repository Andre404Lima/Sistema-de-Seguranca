
🛡️ Sistema de Segurança Wayne Industries
Sistema web para gerenciamento de segurança industrial, desenvolvido com Python + Django. Permite o controle de acesso de usuários, gestão de equipamentos, dispositivos e veículos, movimentação de itens entre locais, e visualização de painéis administrativos personalizados.

🚀 Tecnologias Utilizadas
Backend: Python, Django

Banco de Dados: MySQL

Frontend: HTML, CSS, JavaScript

Admin: Django Admin para gerenciamento interno

🏗️ Funcionalidades

✅ Cadastro e autenticação de usuários com diferentes permissões (funcionário, gerente, administrador, batman e alfred)

✅ Gestão de equipamentos, dispositivos e veículos com associação a locais específicos

✅ Movimentação de itens entre locais com histórico completo

✅ Dashboard com resumos e controles rápidos

✅ Upload e exibição de imagens dos itens cadastrados

✅ Controle de usuários e monitoramento das últimas ações por tipo de usuário

🚀 Futuras melhorias
🚧 Implementar controle de permissões com base em grupos personalizados

🚧 Melhorar interface visual com framework front-end (ex: Bootstrap ou Tailwind)

🚧 Implementar sistema de notificações

🚧 Criar relatórios exportáveis (PDF/Excel)

🚧 Adicionar testes automatizados para rotas críticas

📦 Estrutura do Projeto

projeto_final/

├── core/                    # Aplicação principal

│   ├── admin.py             # Painel administrativo do Django

│   ├── models.py            # Modelos do sistema: Equipamento, Dispositivo, Veículo, etc.


│   ├── views.py             # Lógicas das views para páginas HTML e interações

│   ├── urls.py              # Rotas da aplicação

│   ├── templates/core/      # Templates HTML organizados por tela

│   ├── static/core/         # Arquivos CSS, JS e imagens estáticas

│   └── forms.py             # Formulários do sistema


├── projeto_final/           # Configurações globais do Django

│   ├── settings.py

│   ├── urls.py

│   └── wsgi.py

├── media/                   # Pasta para imagens e arquivos enviados pelos usuários

├── manage.py                # Script de gerenciamento do Django

└── venv/                    # Ambiente virtual Python

🔧 Como rodar o projeto localmente

1️⃣ Clone o repositório


git clone <URL_DO_REPOSITORIO>

cd projeto_final

2️⃣ Crie e ative o ambiente virtual


python -m venv venv

# Windows (PowerShell)

.\venv\Scripts\Activate.ps1

# Linux/macOS

source venv/bin/activate

3️⃣ Instale as dependências


pip install django mysqlclient

4️⃣ Configure o banco de dados MySQL

Edite o arquivo projeto_final/settings.py e configure a seção DATABASES:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wayne_security',
        'USER': 'root',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

5️⃣ Execute as migrações

python manage.py migrate

6️⃣ Inicie o servidor de desenvolvimento

python manage.py runserver

7️⃣ Acesse o sistema via navegador

Abra os endereços:


http://127.0.0.1:8000/admin/
login: batman 
senha: 123456
http://127.0.0.1:8000/login/

users 
funcionario: 
login: andre
senha: 123456
gerente: 
login: gerente
senha: 123456
administradoro: 
login: admin
senha: 123456
batman: 
login: batman 
senha: 123456
alfred:
login: alfred
senha: 123456



🔄 Como restaurar o backup do banco de dados MySQL

1️⃣ Certifique-se que o servidor MySQL está rodando.

2️⃣ Abra o terminal (PowerShell, Terminal etc).

3️⃣ Crie o banco de dados, caso não exista:

mysql -u root -p

Digite a senha do usuário e execute:

sql

CREATE DATABASE IF NOT EXISTS wayne_security CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

EXIT;

4️⃣ Execute o comando para restaurar o backup (fora do prompt MySQL):

mysql -u root -p wayne_security < caminho/para/backup_wayne_security.sql

Substitua caminho/para/backup_wayne_security.sql pelo caminho correto do seu arquivo.

5️⃣ Aguarde a conclusão. O banco estará restaurado.

👨‍💻 Desenvolvido por
Andre Lima
LinkedIn: André Crisóstomo Nobre Lima
