from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configura a aplicação com as variáveis definidas em config.py
app.config.from_object('config.Config')

# Inicializa o banco de dados
db = SQLAlchemy(app)

# Inicializa o Flask-Migrate
migrate = Migrate(app, db)

# Importa os modelos após a inicialização do db e migrate
from app import models

# Importa e registra os blueprints para as rotas
from app.routes.contas_routes import bp as contas_bp
from app.routes.credores_routes import bp as credores_bp

app.register_blueprint(contas_bp)
app.register_blueprint(credores_bp)

# Executa a aplicação
if __name__ == '__main__':
    app.run(debug=True)
