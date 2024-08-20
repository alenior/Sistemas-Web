from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

@app.route('/')
def home():
    return "Bem-vindo ao Sistema de Contas a Pagar!"

if __name__ == '__main__':
    app.run(debug=True)
