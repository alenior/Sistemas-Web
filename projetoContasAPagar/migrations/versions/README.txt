# Diretório de Migrações

Este diretório contém arquivos e configurações para gerenciar migrações do banco de dados usando Flask-Migrate e Alembic.

## Estrutura do Diretório

- **versions/**: Contém arquivos de migração gerados automaticamente. Cada arquivo de migração representa uma mudança no esquema do banco de dados.
- **alembic.ini**: Arquivo de configuração para Alembic, usado para conectar e configurar o banco de dados.
- **env.py**: Configuração do ambiente de migração, incluindo a configuração do banco de dados e a importação dos modelos.
- **README**: Este arquivo, que fornece informações básicas sobre o diretório de migrações.

## Comandos Úteis

- **Inicializar Migrações**: Configura o diretório de migrações.
  ```bash
  flask db init
