from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object('config.Config')  # Carrega configurações padrão
app.config.from_pyfile('instance/config.py', silent=True)  # Sobrescreve com configurações específicas do ambiente
db = SQLAlchemy(app)

@app.route('/')
def index():
    return "Bem-vindo ao sistema de controle de contas a pagar!"


class Credor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255))
    cnpj = db.Column(db.String(18))
    telefone = db.Column(db.String(15))
    email = db.Column(db.String(255))
    endereco = db.Column(db.String(255))

class ContaAPagar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credor_id = db.Column(db.Integer, db.ForeignKey('credor.id'))
    descricao = db.Column(db.String(255))
    valor = db.Column(db.Float)
    data_vencimento = db.Column(db.Date)
    status = db.Column(db.String(20))

@app.route('/api/credores', methods=['GET'])
def get_credores():
    credores = Credor.query.all()
    return jsonify([{
        'id': credor.id,
        'nome': credor.nome
    } for credor in credores])

@app.route('/api/contas', methods=['GET'])
def get_contas():
    credor_id = request.args.get('credor_id')
    status = request.args.get('status')
    contas = ContaAPagar.query.filter_by(credor_id=credor_id, status=status).all()
    return jsonify([{
        'id': conta.id,
        'descricao': conta.descricao,
        'valor': conta.valor,
        'data_vencimento': conta.data_vencimento,
        'status': conta.status
    } for conta in contas])

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Isso cria todas as tabelas conforme definidas nos modelos do SQLAlchemy
    app.run(debug=True)
