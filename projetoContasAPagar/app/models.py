from app import db

class Conta(db.Model):
    __tablename__ = 'contas_a_pagar'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status_conta = db.Column(db.String(50), nullable=False)
    credor_id = db.Column(db.Integer, db.ForeignKey('credores.id'), nullable=False)
    
    # Relacionamento com Credor
    credor = db.relationship('Credor', back_populates='contas')

class Credor(db.Model):
    __tablename__ = 'credores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    
    # Relacionamento com Contas
    contas = db.relationship('Conta', back_populates='credor')
