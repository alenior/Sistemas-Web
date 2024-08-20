from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config.from_object('config.Config')
    db.init_app(app)
    migrate.init_app(app, db)

    # Certifique-se de que os blueprints estão sendo registrados
    from app.routes.contas_routes import bp as contas_bp
    from app.routes.credores_routes import bp as credores_bp
    app.register_blueprint(contas_bp)
    app.register_blueprint(credores_bp)

    return app
