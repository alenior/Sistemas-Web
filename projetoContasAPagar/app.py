from flask import Flask, render_template, url_for, request, redirect, flash, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from weasyprint import HTML
import io
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pdfkit

path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'  # Caminho para o executável do wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# Importar a instância de db e migrate do pacote
from projetoContasAPagar import create_app, db
from projetoContasAPagar.models import ContaAPagar, Credor  # Certifique-se de que este caminho está correto

app = create_app()

# Defina a chave secreta para sua aplicação
app.config['SECRET_KEY'] = 'minha_chave_secreta'

# Modelos do banco de dados
STATUS_MAP = {
    'pago': 'PAGO',
    'a_vencer': 'A VENCER',
    'vencido': 'VENCIDO'
}

def format_currency(value):
    """Formata um valor como moeda (R$)."""
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

# Registrar o filtro no Jinja2
app.jinja_env.filters['format_currency'] = format_currency

# Rota da página inicial
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/credores')
def get_creditors():
    credores = Credor.query.all()
    return render_template('creditors.html', credores=credores)

@app.route('/export-creditors-pdf')
def export_creditors_pdf():
    credores = Credor.query.all()  # Obtenha a lista de credores

    # Renderize o template HTML para o PDF
    rendered = render_template('creditors_pdf.html', credores=credores)

    # Crie o PDF a partir do HTML
    pdf = HTML(string=rendered).write_pdf()

    # Envie o PDF para o usuário
    return send_file(io.BytesIO(pdf), download_name='credores.pdf', as_attachment=True)

@app.route('/contas')
def get_bills():
    contas = ContaAPagar.query.all()
    return render_template('bills.html', contas=contas)

@app.route('/export-bills-pdf')
def export_bills_pdf():
    contas = ContaAPagar.query.all()  # Obtenha a lista de contas a pagar

    # Renderize o template HTML para o PDF
    rendered = render_template('bills_pdf.html', contas=contas, STATUS_MAP=STATUS_MAP)

    # Crie o PDF a partir do HTML
    pdf = HTML(string=rendered).write_pdf()

    # Envie o PDF para o usuário
    return send_file(io.BytesIO(pdf), as_attachment=True, download_name='contas_a_pagar.pdf')

@app.route('/contas-por-periodo', methods=['GET', 'POST'])
def bills_by_period():
    contas = []

    # Se for um GET, definimos as datas padrão como hoje
    data_inicio = date.today().strftime('%Y-%m-%d')
    data_fim = date.today().strftime('%Y-%m-%d')
    credor_id = request.args.get('credor_id', None)
    status_conta = request.args.get('status_conta', None)

    if request.method == 'POST':
        # Supor que você receba as datas no formato 'YYYY-MM-DD'
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        credor_id = request.form.get('credor_id')
        status_conta = request.form.get('status_conta')

        if data_inicio and data_fim:
        # Converter as datas para o formato necessário
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            # Consulta ao banco de dados filtrando pelo período
            contas = ContaAPagar.query.filter(
                ContaAPagar.data_vencimento.between(data_inicio, data_fim)
            )

            if credor_id:
                contas = contas.filter_by(credor_id=credor_id)
            
            if status_conta:
                contas = contas.filter_by(status_conta=status_conta)

            contas = contas.options(db.joinedload(ContaAPagar.credor_relacionado)).all()

    credores = Credor.query.all()
    statuses = STATUS_MAP.keys()

    return render_template(
        'bills_by_period.html', 
        contas=contas, 
        data_inicio=data_inicio, 
        data_fim=data_fim, 
        credores=credores,
        statuses=statuses,
        STATUS_MAP=STATUS_MAP  # Adiciona o STATUS_MAP ao contexto do template
    )

@app.route('/exportar_contas_por_periodo_pdf', methods=['GET'])
def export_bills_by_period_pdf():
    # Ajuste a consulta conforme necessário para filtrar as contas por período
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    contas_query = db.session.query(ContaAPagar).filter(ContaAPagar.data_vencimento.between(data_inicio, data_fim))

    # Inclua filtros adicionais de credor e status se aplicável
    credor_id = request.args.get('credor_id')
    status_conta = request.args.get('status_conta')

    if credor_id:
        contas_query = contas_query.filter_by(credor_id=credor_id)
    if status_conta:
        contas_query = contas_query.filter_by(status_conta=status_conta)

    contas = contas_query.all()

    # Renderizar o template para o PDF
    rendered = render_template('bills_by_period_pdf.html', contas=contas, STATUS_MAP=STATUS_MAP)
    
    # Gerar o PDF usando o HTML renderizado
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    # Retornar o PDF como arquivo para download
    return send_file(io.BytesIO(pdf), download_name='relatorio_contas_por_periodo.pdf', as_attachment=True)

@app.route('/contas-por-credor', methods=['GET', 'POST'])
def contas_por_credor():
    if request.method == 'POST':
        credor_id = request.form.get('credor_id')
        contas = ContaAPagar.query.filter_by(credor_id=credor_id).all()
        credores = Credor.query.all() # Carregar a lista de credores para o formulário
        return render_template('contas_por_credor.html', contas=contas, credores=credores)
    
    credores = Credor.query.all() # Carregar a lista de credores para o formulário
    return render_template('contas_por_credor.html', contas=[], credores=credores)

@app.route('/exportar_contas_por_credor_pdf', methods=['GET'])
def export_bills_by_creditor_pdf():
    credor_id = request.args.get('credor_id')
    # Inclua filtros adicionais de status se aplicável
    status_conta = request.args.get('status_conta')

    # Ajuste a consulta para filtrar as contas por credor
    contas_query = db.session.query(ContaAPagar).join(Credor).filter(ContaAPagar.credor_id == credor_id)

    if status_conta:
        contas_query = contas_query.filter_by(status_conta=status_conta)

    contas = contas_query.all()

    # Renderizar o template para o PDF
    rendered = render_template('bills_by_creditor_pdf.html', contas=contas, STATUS_MAP=STATUS_MAP)
    
    # Gerar o PDF usando o HTML renderizado
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    # Retornar o PDF como arquivo para download
    return send_file(io.BytesIO(pdf), download_name='relatorio_contas_por_credor.pdf', as_attachment=True)


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

@app.route('/delete_credor/<int:id>', methods=['POST'])
def delete_credor(id):
    credor = Credor.query.get_or_404(id)
    db.session.delete(credor)
    db.session.commit()
    flash('Credor excluído com sucesso!', 'success')
    return redirect(url_for('get_creditors')) # Redireciona para a página de listagem de credores

@app.route('/add_conta', methods=['GET', 'POST'])
def add_conta():
    credores = Credor.query.all()
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

@app.route('/delete_conta/<int:id>', methods=['POST'])
def delete_conta(id):
    conta = ContaAPagar.query.get_or_404(id)
    db.session.delete(conta)
    db.session.commit()
    flash('Conta excluída com sucesso!', 'success')
    return redirect(url_for('get_bills'))  # Redireciona para a página de listagem de contas


if __name__ == '__main__':
    app.run(debug=True)
