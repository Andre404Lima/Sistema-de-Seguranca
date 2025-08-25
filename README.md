🛡️ Sistema de Segurança Wayne Industries  
Sistema web para gerenciamento de segurança industrial, desenvolvido com Python + Django. Permite o controle de acesso de usuários, gerenciamento de equipamentos, dispositivos e veículos, bem como visualização de movimentações e painéis administrativos personalizados.

🚀 Tecnologias Utilizadas  
- Backend: Python, Django  
- Banco de Dados: MySQL  
- Frontend: HTML, CSS, JavaScript  
- Admin: Django Admin para gerenciamento interno  

🏗️ Funcionalidades  
✅ Cadastro e autenticação de usuários com diferentes permissões (funcionário, gerente, administrador)  
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

├── core/ # Aplicação principal  
│   ├── admin.py # Painel administrativo do Django  
│   ├── models.py # Modelos do sistema: Equipamento, Dispositivo, Veículo, etc.  
│   ├── views.py # Lógicas das views para páginas HTML e interações  
│   ├── urls.py # Rotas da aplicação  
│   ├── templates/core/ # Templates HTML organizados por tela  
│   ├── static/core/ # Arquivos CSS, JS e imagens estáticas  
│   └── forms.py # Formulários do sistema  

├── projeto_final/ # Configurações globais do Django  
│   ├── settings.py  
│   ├── urls.py  
│   └── wsgi.py  

├── media/ # Pasta para imagens e arquivos enviados pelos usuários  

├── manage.py # Script de gerenciamento do Django  

└── venv/ # Ambiente virtual Python  

🔧 Como rodar o projeto localmente  

1️⃣ Clone o repositório  
```bash
git clone <URL_DO_REPOSITORIO>
cd projeto_final
2️⃣ Crie e ative o ambiente virtual

bash
Copiar
Editar
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate
3️⃣ Instale as dependências

bash
Copiar
Editar
pip install django mysqlclient
4️⃣ Configure o banco de dados MySQL no settings.py

python
Copiar
Editar
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

bash
Copiar
Editar
python manage.py migrate
6️⃣ Crie um superusuário

bash
Copiar
Editar
python manage.py createsuperuser
7️⃣ Inicie o servidor de desenvolvimento

bash
Copiar
Editar
python manage.py runserver
8️⃣ Acesse o sistema via navegador
http://127.0.0.1:8000/admin/

👨‍💻 Desenvolvido por
Andre Lima
LinkedIn: André Crisóstomo Nobre Lima

yaml
Copiar
Editar
