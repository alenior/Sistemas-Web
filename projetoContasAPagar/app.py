from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/contas_a_pagar'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos do banco de dados
class Credor(db.Model):
    __tablename__ = 'credor'  # Nome da tabela no banco de dados
    
    id = db.Column(db.Integer, primary_key=True)  # Coluna ID
    nome = db.Column(db.String(100), nullable=False)  # Coluna Nome
    cnpj = db.Column(db.String(18), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    contas = db.relationship('ContaAPagar', backref='credor_relacionado', lazy=True)

    def __repr__(self):
        return f'<Credor {self.nome}>'

STATUS_MAP = {
    'pago': 'PAGO',
    'a_vencer': 'A VENCER',
    'vencido': 'VENCIDO'
}

class ContaAPagar(db.Model):
    __tablename__ = 'conta_a_pagar'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)  # A data de vencimento foi adicionada
    status_conta = db.Column(db.String(20), nullable=False)
    credor_id = db.Column(db.Integer, db.ForeignKey('credor.id'), nullable=False)
    credor = db.relationship('Credor', backref=db.backref('contas_relacionadas', lazy=True))

    def get_status_display(self):
        return STATUS_MAP.get(self.status_conta, 'Desconhecido')

    def __repr__(self):
        return f'<ContaAPagar {self.descricao}>'

# Rota da página inicial
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/credores')
def get_creditors():
    credores = Credor.query.all()
    return render_template('creditors.html', credores=credores)

@app.route('/contas')
def get_bills():
    contas = ContaAPagar.query.all()
    return render_template('bills.html', contas=contas)

# Rota para listar contas por período
@app.route('/contas-por-periodo', methods=['GET', 'POST'])
def bills_by_period():
    contas = []

    if request.method == 'POST':
        # Supor que você receba as datas no formato 'YYYY-MM-DD'
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

        if data_inicio and data_fim:
        # Converter as datas para o formato necessário
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

            # Consulta ao banco de dados filtrando pelo período
            contas = ContaAPagar.query.filter(ContaAPagar.data_vencimento >= data_inicio,
                                          ContaAPagar.data_vencimento <= data_fim).all()

    return render_template('bills_by_period.html', contas=contas)

# Rota para listar contas por credor
@app.route('/contas-por-credor', methods=['GET', 'POST'])
def contas_por_credor():
    if request.method == 'POST':
        credor_id = request.form.get('credor_id') # Correção aqui
        contas = ContaAPagar.query.filter_by(credor_id=credor_id).all()
        credores = Credor.query.all() # Carregar a lista de credores para o formulário
        return render_template('contas_por_credor.html', contas=contas, credores=credores)
    
    credores = Credor.query.all() # Carregar a lista de credores para o formulário
    return render_template('contas_por_credor.html', contas=[], credores=credores)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)
