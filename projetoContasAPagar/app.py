from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Defina a chave secreta para sua aplicação
app.config['SECRET_KEY'] = 'minha_chave_secreta'

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
    contas = db.relationship('ContaAPagar', back_populates='credor_relacionado', lazy=True)

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
    credor_relacionado = db.relationship('Credor', back_populates='contas', lazy=True)

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

# Incluir um novo credor
@app.route('/add_credor', methods=['GET', 'POST'])
def add_credor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cnpj = request.form.get('cnpj')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        endereco = request.form.get('endereco')
        novo_credor = Credor(nome=nome, cnpj=cnpj, telefone=telefone, email=email, endereco=endereco)
        db.session.add(novo_credor)
        db.session.commit()
        flash('Credor adicionado com sucesso!', 'success')
        return redirect(url_for('get_creditors'))  # Redireciona para a página de listagem de credores
    return render_template('add_credor.html')

# Alterar um credor existente
@app.route('/edit_credor/<int:id>', methods=['GET', 'POST'])
def edit_credor(id):
    credor = Credor.query.get_or_404(id)
    if request.method == 'POST':
        credor.nome = request.form.get('nome')
        credor.cnpj = request.form.get('cnpj')
        credor.telefone = request.form.get('telefone')
        credor.email = request.form.get('email')
        credor.endereco = request.form.get('endereco')

        db.session.commit()
        flash('Credor alterado com sucesso!', 'success')
        return redirect(url_for('get_creditors'))  # Redireciona para a página de listagem de credores
    return render_template('edit_credor.html', credor=credor)

# Excluir um credor
@app.route('/delete_credor/<int:id>', methods=['POST'])
def delete_credor(id):
    credor = Credor.query.get_or_404(id)
    db.session.delete(credor)
    db.session.commit()
    flash('Credor excluído com sucesso!', 'success')
    return redirect(url_for('get_creditors')) # Redireciona para a página de listagem de credores

# Incluir uma nova conta
@app.route('/add_conta', methods=['GET', 'POST'])
def add_conta():
    credores = Credor.query.all() # Antes do último return?
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        valor = request.form.get('valor').replace(',', '.')  # Substituir vírgula por ponto
        valor = float(valor)  # Converter para float após substituir a vírgula
        data_vencimento = request.form.get('data_vencimento')
        status_conta = request.form.get('status_conta')
        credor_id = request.form.get('credor_id')

        nova_conta = ContaAPagar(
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            status_conta=status_conta,
            credor_id=credor_id
        )

        db.session.add(nova_conta)
        db.session.commit()
        flash('Conta adicionada com sucesso!', 'success')
        return redirect(url_for('get_bills'))  # Redireciona para a página de listagem de contas
    
    return render_template('add_conta.html', credores=credores, STATUS_MAP=STATUS_MAP)

# Alterar uma conta existente
@app.route('/edit_conta/<int:id>', methods=['GET', 'POST'])
def edit_conta(id):
    conta = ContaAPagar.query.get_or_404(id)
    credores = Credor.query.all()

    if request.method == 'POST':
        conta.descricao = request.form.get('descricao')

        # Converte o valor substituindo vírgula por ponto
        valor_str = request.form.get('valor').replace(',', '.')
        try:
            conta.valor = float(valor_str)
        except ValueError:
            flash('O valor fornecido não é válido.', 'error')
            return render_template('edit_conta.html', conta=conta, credores=credores)

        conta.data_vencimento = request.form.get('data_vencimento')
        conta.status_conta = request.form.get('status_conta')
        conta.credor_id = request.form.get('credor_id')

        db.session.commit()
        flash('Conta alterada com sucesso!', 'success')
        return redirect(url_for('get_bills'))  # Redireciona para a página de listagem de contas
    
    return render_template('edit_conta.html', conta=conta, credores=credores, STATUS_MAP=STATUS_MAP)

# Excluir uma conta
@app.route('/delete_conta/<int:id>', methods=['POST'])
def delete_conta(id):
    conta = ContaAPagar.query.get_or_404(id)
    db.session.delete(conta)
    db.session.commit()
    flash('Conta excluída com sucesso!', 'success')
    return redirect(url_for('bills'))  # Redireciona para a página de listagem de contas


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)
