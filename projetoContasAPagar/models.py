from projetoContasAPagar import db

# Modelos do banco de dados
class Credor(db.Model):
    __tablename__ = 'credor'  # Nome da tabela no banco de dados
    id = db.Column(db.Integer, primary_key=True)  # Coluna ID
    nome = db.Column(db.String(100), nullable=False)  # Coluna Nome
    cnpj = db.Column(db.String(18), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
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
    