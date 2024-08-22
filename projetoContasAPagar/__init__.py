# projetoContasAPagar/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/contas_a_pagar'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'minha_chave_secreta'

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from projetoContasAPagar import models  # Certifique-se de importar os modelos aqui para que eles sejam reconhecidos

    return app
