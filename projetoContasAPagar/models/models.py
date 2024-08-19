from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Credor(db.Model):
    __tablename__ = 'credor'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Credor {self.nome}>'

class ContaAPagar(db.Model):
    __tablename__ = 'contas_a_pagar'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    status_conta = db.Column(db.String(50))  # Nome atualizado da coluna
    credor_id = db.Column(db.Integer, db.ForeignKey('credor.id'), nullable=False)
    credor = db.relationship('Credor', backref=db.backref('contas', lazy=True))

    def __repr__(self):
        return f'<ContaAPagar {self.descricao} - {self.status_conta}>'
