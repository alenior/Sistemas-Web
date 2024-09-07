from flask import Flask, render_template, url_for, request, redirect, flash, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from weasyprint import HTML, CSS
from io import BytesIO
from flask_weasyprint import HTML, render_pdf
from sqlalchemy import case, func

import pdfkit
import io
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Caminho para o executável do wkhtmltopdf
path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# Importar a instância de db e migrate do pacote
from projetoContasAPagar import create_app, db
from projetoContasAPagar.models import ContaAPagar, Credor

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

def atualizar_status_contas():
    contas_a_vencer = ContaAPagar.query.filter_by(status_conta='a_vencer').all()
    hoje = date.today()

    for conta in contas_a_vencer:
        if conta.data_vencimento < hoje:
            conta.status_conta = 'vencido'
            db.session.add(conta)
    
    db.session.commit()

@app.template_filter('format_currency')
def format_currency(value):
    if value is None or value == 'undefined':
        return "R$ 0,00"
    try:
        return "R$ {:.2f}".format(value).replace('.', ',')
    except (TypeError, ValueError):
        return "R$ 0,00"

# Rota da página inicial
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/credores')
def get_creditors():
    credores = Credor.query.order_by(Credor.id.desc()).all()
    # return render_template('creditors.html', credores=credores)

    sort_by = request.args.get('sort_by', 'id')  # Ordena por 'id' por padrão
# Ordena de forma decrescente por padrão
    order = request.args.get('order', 'desc')

    if sort_by == 'nome':
        if order == 'asc':
            credores = Credor.query.order_by(Credor.nome.asc()).all()
        else:
            credores = Credor.query.order_by(Credor.nome.desc()).all()
    else:  # Ordenação por ID
        if order == 'asc':
            credores = Credor.query.order_by(Credor.id.asc()).all()
        else:
            credores = Credor.query.order_by(Credor.id.desc()).all()

    return render_template('creditors.html', credores=credores)


@app.route('/export-creditors-pdf')
def export_creditors_pdf():
    credores = Credor.query.all()  # Obtenha a lista de credores

    # Renderize o template HTML para o PDF
    rendered = render_template('creditors_pdf.html', credores=credores)

    # CSS customizado para centralizar o título
    centralize_css = CSS(string='''
        body {
            font-size: 12px;
        }
        .centralizar {
            text-align: center;
        }
    ''')

    # Crie o PDF a partir do HTML
    pdf = HTML(string=rendered).write_pdf(stylesheets=[centralize_css], presentational_hints=True)

    # Envie o PDF para o usuário
    return send_file(io.BytesIO(pdf), download_name='credores.pdf', as_attachment=True)


@app.route('/contas')
def get_bills():
    # Atualiza o status das contas antes de realizar a consulta
    atualizar_status_contas()
    
    # Define a ordem dos status
    status_order = {
        'vencido': 1,
        'a_vencer': 2,
        'pago': 3
    }

    # Consulta ordenando as contas pelo status usando a ordem definida
    contas = ContaAPagar.query.order_by(
        case(
            *[(ContaAPagar.status_conta == status, order) for status, order in status_order.items()]
        ).asc(),
        ContaAPagar.data_vencimento.asc()
    ).all()

    # Calcula os valores para multa e juros
    for conta in contas:
        if conta.status_conta == 'pago':
            # Se a conta foi paga, calcula multa e juros, se aplicável
            if conta.data_pagamento and conta.data_pagamento > conta.data_vencimento:
                dias_atraso = (conta.data_pagamento - conta.data_vencimento).days
                conta.multa = conta.valor * 0.01  # 1% de multa
                conta.juros = conta.valor * 0.002 * dias_atraso  # 0,2% por dia de atraso
            else:
                conta.multa = 0.00
                conta.juros = 0.00
        else:
            # Para status 'a vencer' ou 'vencido', multa e juros são 0.00
            conta.multa = 0.00
            conta.juros = 0.00

    return render_template('bills.html', contas=contas, STATUS_MAP=STATUS_MAP)


@app.route('/export-bills-pdf')
def export_bills_pdf():
    # Ordem de prioridade dos status
    status_order = {'vencido': 1, 'a_vencer': 2, 'pago': 3}

    # Obtenha a lista de contas a pagar e ordene por status
    contas_query = ContaAPagar.query

    # Ordenar por status utilizando a ordem definida
    status_case = db.case(
        *[(ContaAPagar.status_conta == status, rank) for status, rank in status_order.items()],
        else_=len(status_order) + 1
    )

    contas = contas_query.order_by(status_case).all()

    # Renderize o template HTML para o PDF
    rendered = render_template(
        'bills_pdf.html', contas=contas, STATUS_MAP=STATUS_MAP)
    
    # CSS customizado para orientação paisagem
    landscape_css = CSS(string='''
        @page {
            size: A4 landscape;
            margin: 1cm;
        }
        body {
            font-size: 12px;
        }
        .centralizar {
            text-align: center;                
        }
    ''')

    # Crie o PDF a partir do HTML
    pdf = HTML(string=rendered).write_pdf(stylesheets=[landscape_css], presentational_hints=True)

    # Use io.BytesIO para armazenar o PDF em memória
    pdf_io = io.BytesIO(pdf)

    # Envie o PDF para o usuário
    return send_file(pdf_io, as_attachment=True, download_name='contas_a_pagar.pdf')


@app.route('/contas-por-periodo')
def bills_by_period():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    credor_id = request.args.get('credor_id')
    status_conta = request.args.get('status_conta')

    hoje = datetime.now()

    # Primeiro dia do mês anterior
    if not data_inicio:
        primeiro_dia_mes_anterior = hoje.replace(day=1) - timedelta(days=1)
        data_inicio = primeiro_dia_mes_anterior.replace(day=1).strftime('%Y-%m-%d')
    
    # Último dia do mês posterior
    if not data_fim:
        # Primeiro dia do mês seguinte
        primeiro_dia_mes_posterior = (hoje.replace(day=1) + timedelta(days=31)).replace(day=1)
        # Último dia do mês seguinte
        ultimo_dia_mes_posterior = (primeiro_dia_mes_posterior + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        data_fim = ultimo_dia_mes_posterior.strftime('%Y-%m-%d')

     # Ordenação personalizada por status
    status_order = {
        'vencido': 1,
        'a_vencer': 2,
        'pago': 3
    }

    # Filtro básico por data
    query = db.session.query(ContaAPagar).filter(
        ContaAPagar.data_vencimento.between(data_inicio, data_fim)
    )

    # Filtro por credor, se fornecido
    if credor_id:
        query = query.filter(ContaAPagar.credor_id == credor_id)

    # Filtro por status, se fornecido
    if status_conta:
        query = query.filter(ContaAPagar.status_conta == status_conta)

   # Adicionar ordenação personalizada
    contas = query.order_by(
        case(
            *[
                (ContaAPagar.status_conta == 'vencido', 1),
                (ContaAPagar.status_conta == 'a_vencer', 2),
                (ContaAPagar.status_conta == 'pago', 3)
            ]
        ),
        ContaAPagar.data_vencimento
    ).all()

    # Verifique se todos os campos numéricos estão definidos
    for conta in contas:
        conta.valor = conta.valor or 0
        conta.multa = conta.multa or 0
        conta.juros = conta.juros or 0

    credores = Credor.query.order_by(Credor.nome).all()

    return render_template('bills_by_period.html', contas=contas, credores=credores, data_inicio=data_inicio, data_fim=data_fim, STATUS_MAP=STATUS_MAP)


@app.route('/exportar_contas_por_periodo_pdf', methods=['GET'])
def export_bills_by_period_pdf():
    # Ajuste a consulta conforme necessário para filtrar as contas por período
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    # Inclua filtros adicionais de credor e status se aplicável
    credor_id = request.args.get('credor_id')
    status_conta = request.args.get('status_conta')

    # Ordem de prioridade dos status
    status_order = {'vencido': 1, 'a_vencer': 2, 'pago': 3}

    # Verificar e converter as datas de string para objetos date
    if data_inicio and data_fim:
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            return "Formato de data inválido", 400

        # Construir a consulta com filtros
        contas_query = db.session.query(ContaAPagar).filter(
            ContaAPagar.data_vencimento.between(data_inicio, data_fim)
        )

        if credor_id:
            contas_query = contas_query.filter_by(credor_id=credor_id)

        if status_conta:
            contas_query = contas_query.filter_by(status_conta=status_conta)

        # Ordenar por status utilizando a ordem definida
        status_case = db.case(
            *[(ContaAPagar.status_conta == status, rank) for status, rank in status_order.items()],
            else_=len(status_order) + 1
        )

        contas = contas_query.order_by(status_case).all()

        # Renderizar o template para o PDF
        rendered = render_template(
            'bills_by_period_pdf.html', contas=contas, STATUS_MAP=STATUS_MAP)
        
        # Gerar o PDF usando o HTML renderizado
        pdf_options = {
            'page-size': 'A4',
            'orientation': 'Landscape',
            'no-outline': None
        }

        # Gerar o PDF usando o HTML renderizado
        pdf = pdfkit.from_string(rendered, False, configuration=config, options=pdf_options)

        # Retornar o PDF como arquivo para download
        return send_file(io.BytesIO(pdf), download_name='relatorio_contas_por_periodo.pdf', as_attachment=True)

    else:
        return "Datas inválidas ou não fornecidas", 400


@app.route('/contas_por_credor', methods=['GET'])
def contas_por_credor():
    credores = Credor.query.all()

    # Adicionar filtros se existirem
    credor_id = request.args.get('credor_id')
    status_conta = request.args.get('status_conta')

    # Inicializa a consulta
    contas_query = db.session.query(
        Credor.nome.label('credor'),
        func.count(ContaAPagar.id).label('total_contas'),
        func.sum(ContaAPagar.valor_total).label('valor_total'),
        func.avg(ContaAPagar.valor_total).label('valor_medio'),
        func.sum(case([(ContaAPagar.status_conta == 'vencido', ContaAPagar.valor_total)], else_=0)).label('valor_vencidas'),
        func.sum(case([(ContaAPagar.status_conta == 'a_vencer', ContaAPagar.valor_total)], else_=0)).label('valor_a_vencer'),
        func.sum(case([(ContaAPagar.status_conta == 'pago', ContaAPagar.valor_total)], else_=0)).label('valor_pagas')
    ).join(Credor, ContaAPagar.credor_id == Credor.id)

    # Aplica os filtros se existirem
    if credor_id:
        contas_query = contas_query.filter(ContaAPagar.credor_id == credor_id)
    if status_conta:
        contas_query = contas_query.filter(ContaAPagar.status_conta == status_conta)

    # Agrupar os resultados pelo nome do credor
    contas_query = contas_query.group_by(Credor.nome)

    # Ordenar pelo valor total em ordem decrescente
    contas = contas_query.order_by(func.sum(ContaAPagar.valor_total).desc()).all()

    credor_id_selecionado = request.args.get('credor_id')
    return render_template('contas_por_credor.html', contas=contas, credores=credores, STATUS_MAP=STATUS_MAP, credor_id_selecionado=int(credor_id_selecionado) if credor_id_selecionado else None)


@app.route('/exportar_contas_por_credor_pdf', methods=['GET'])
def export_bills_by_creditor_pdf():
    # Consulta para agrupar as contas por credor e calcular as métricas
    contas_query = db.session.query(
        Credor.nome.label('credor'),
        func.count(ContaAPagar.id).label('total_contas'),
        func.sum(ContaAPagar.valor).label('valor_total'),
        func.avg(ContaAPagar.valor).label('valor_medio'),
        func.count(case([(ContaAPagar.status_conta == 'vencido', 1)])).label('total_vencidas'),
        func.sum(case([(ContaAPagar.status_conta == 'vencido', ContaAPagar.valor)])).label('valor_vencidas'),
        func.count(case([(ContaAPagar.status_conta == 'a_vencer', 1)])).label('total_a_vencer'),
        func.sum(case([(ContaAPagar.status_conta == 'a_vencer', ContaAPagar.valor)])).label('valor_a_vencer'),
        func.count(case([(ContaAPagar.status_conta == 'pago', 1)])).label('total_pagas'),
        func.sum(case([(ContaAPagar.status_conta == 'pago', ContaAPagar.valor)])).label('valor_pagas')
    ).join(Credor).group_by(Credor.nome)

    # Aplica os filtros se existirem
    credor_id = request.args.get('credor_id')
    status_conta = request.args.get('status_conta')

    # Cria a consulta base
    contas_query = db.session.query(ContaAPagar).join(
        Credor).filter(Credor.id == ContaAPagar.credor_id)

    # Aplica os filtros se existirem
    if credor_id:
        contas_query = contas_query.filter(ContaAPagar.credor_id == credor_id)
    if status_conta:
        contas_query = contas_query.filter(
            ContaAPagar.status_conta == status_conta)

    # Ordenar pelo valor total em ordem decrescente
    contas = contas_query.order_by(func.sum(ContaAPagar.valor).desc()).all()

    # Renderiza o template para o PDF
    rendered = render_template(
        'bills_by_creditor_pdf.html', contas=contas, STATUS_MAP=STATUS_MAP)

    # Gera o PDF usando o HTML renderizado
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    # Retorna o PDF como arquivo para download
    return send_file(io.BytesIO(pdf), download_name='relatorio_contas_por_credor.pdf', as_attachment=True)


@app.route('/add_credor', methods=['GET', 'POST'])
def add_credor():
    if request.method == 'POST':
        nome = request.form.get('nome')

        cnpj = request.form.get('cnpj')
        # (Opcional) Se preferir salvar o CNPJ sem formatação:
        # cnpj = re.sub(r'\D', '', cnpj)  # Remove todos os caracteres não numéricos

        telefone = request.form.get('telefone')
        # (Opcional) Se preferir salvar o telefone sem formatação:
        # telefone = re.sub(r'\D', '', telefone)  # Remove todos os caracteres não numéricos

        email = request.form.get('email')
        endereco = request.form.get('endereco')

        novo_credor = Credor(nome=nome, cnpj=cnpj,
                             telefone=telefone, email=email, endereco=endereco)
        db.session.add(novo_credor)
        db.session.commit()
        flash('Credor adicionado com sucesso!', 'success')
        # Redireciona para a página de listagem de credores
        return redirect(url_for('get_creditors'))
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
        # Redireciona para a página de listagem de credores
        return redirect(url_for('get_creditors'))
    return render_template('edit_credor.html', credor=credor)


@app.route('/delete_credor/<int:id>', methods=['POST'])
def delete_credor(id):
    credor = Credor.query.get_or_404(id)
    db.session.delete(credor)
    db.session.commit()
    flash('Credor excluído com sucesso!', 'success')
    # Redireciona para a página de listagem de credores
    return redirect(url_for('get_creditors'))


@app.route('/add_conta', methods=['GET', 'POST'])
def add_conta():
    credores = Credor.query.all()

    # Obter a data atual
    data_atual = datetime.today().date().strftime('%Y-%m-%d')

    if request.method == 'POST':
        descricao = request.form.get('descricao')
        valor = request.form.get('valor').replace(
            ',', '.')  # Substituir vírgula por ponto
        valor = float(valor)  # Converter para float após substituir a vírgula

        # Usar a data do formulário ou a data atual, se não fornecida
        data_vencimento = request.form.get('data_vencimento') or data_atual

        credor_id = request.form.get('credor_id')

        # Cria uma nova conta a pagar com os dados fornecidos
        nova_conta = ContaAPagar(
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            credor_id=credor_id
        )

        try:
            db.session.add(nova_conta)
            db.session.commit()
            flash('Conta adicionada com sucesso!', 'success')
            return redirect(url_for('listar_contas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar conta: {str(e)}', 'danger')
            return redirect(url_for('get_bills'))
        
    # Renderiza o template com a lista de credores e o mapa de status
    return render_template('add_conta.html', credores=credores, STATUS_MAP=STATUS_MAP, data_atual=data_atual)


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
        conta.data_pagamento = request.form['data_pagamento'] or None

        db.session.commit()
        flash('Conta alterada com sucesso!', 'success')
        # Redireciona para a página de listagem de contas
        return redirect(url_for('get_bills'))

    return render_template('edit_conta.html', conta=conta, credores=credores, STATUS_MAP=STATUS_MAP)


@app.route('/delete_conta/<int:id>', methods=['POST'])
def delete_conta(id):
    conta = ContaAPagar.query.get_or_404(id)
    db.session.delete(conta)
    db.session.commit()
    flash('Conta excluída com sucesso!', 'success')
    # Redireciona para a página de listagem de contas
    return redirect(url_for('get_bills'))


if __name__ == '__main__':
    app.run(debug=True)