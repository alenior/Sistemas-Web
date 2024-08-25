### Apresentação: Sistema Web de Controle de Contas a Pagar

---

## a) Descrição dos Requisitos Funcionais

### Funcionalidades Principais

1. **Gestão de Credores**
   - Cadastro de credores (nome, CNPJ, telefone, e-mail, endereço).
   - Edição de credores.
   - Exclusão de credores.
   - Consulta de lista de credores.

2. **Gestão de Contas a Pagar**
   - Cadastro de contas a pagar (credor, descrição, valor, data de vencimento, status).
   - Edição de contas a pagar.
   - Exclusão de contas a pagar.
   - Consulta de contas a pagar.

3. **Consultas e Relatórios**
   - Relação de contas a pagar em um determinado período.
   - Relação de contas pagas em um determinado período.
   - Contas de um determinado credor em um determinado status (pagas, em atraso, a pagar).
   - Relação de credores.

4. **API**
   - Serviço que recebe a identificação de um credor e o status de uma conta e retorna todos os títulos daquele credor naquela situação.

---

## b) Modelo do Banco de Dados

### Tabelas e Relacionamentos

1. **Tabela Credores**
   - **ID** (PK): Integer, Auto Increment
   - **Nome**: Varchar(255)
   - **CNPJ**: Varchar(18)
   - **Telefone**: Varchar(15)
   - **Email**: Varchar(255)
   - **Endereco**: Varchar(255)

2. **Tabela ContasAPagar**
   - **ID** (PK): Integer, Auto Increment
   - **CredorID** (FK): Integer
   - **Descricao**: Varchar(255)
   - **Valor**: Decimal(10,2)
   - **DataVencimento**: Date
   - **Status**: Varchar(20) (Valores possíveis: "a pagar", "paga", "em atraso")

### Relacionamento
   - **ContasAPagar.CredorID** referencia **Credores.ID**

---

## c) Requisitos Não-Funcionais e Tecnologias Utilizadas

### Requisitos Não-Funcionais

1. **Segurança**: Autenticação e autorização para acesso ao sistema.
2. **Usabilidade**: Interface amigável e intuitiva.
3. **Performance**: Resposta rápida às consultas e operações.
4. **Escalabilidade**: Capacidade de lidar com aumento no número de usuários e dados.
5. **Manutenibilidade**: Código bem documentado e organizado para facilitar manutenção e melhorias.

### Tecnologias Utilizadas

1. **Frontend**
   - **HTML**: Estrutura das páginas web.
   - **CSS**: Estilização das páginas web.
   - **JavaScript**: Interatividade e dinamismo no frontend.
   - **React.js**: Biblioteca JavaScript para construção de interfaces de usuário.

2. **Backend**
   - **Python**: Linguagem de programação para lógica de negócio.
   - **Flask**: Framework web para desenvolvimento do backend e APIs.

3. **Banco de Dados**
   - **MySQL**: Sistema de gerenciamento de banco de dados relacional.

4. **API**
   - **RESTful API**: Interface de comunicação para a integração com outros sistemas.

5. **Servidor**
   - **Nginx**: Servidor web para servir a aplicação.

6. **Controle de Versão**
   - **Git**: Controle de versão para gerenciamento do código-fonte.

---

## Exemplo de Código

### Frontend (React.js)

```javascript
// Credores.js
import React, { useState, useEffect } from 'react';

function Credores() {
    const [credores, setCredores] = useState([]);

    useEffect(() => {
        fetch('/api/credores')
            .then(response => response.json())
            .then(data => setCredores(data));
    }, []);

    return (
        <div>
            <h1>Lista de Credores</h1>
            <ul>
                {credores.map(credor => (
                    <li key={credor.id}>{credor.nome}</li>
                ))}
            </ul>
        </div>
    );
}

export default Credores;
```

### Backend (Flask)

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/contas_a_pagar'
db = SQLAlchemy(app)

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
    db.create_all()
    app.run(debug=True)
```

---

## Fluxo de Navegação

1. **Página Inicial**: Acesso às principais funcionalidades (Cadastro de Credores, Contas a Pagar, Relatórios).
2. **Cadastro de Credores**: Formulário para adicionar/editar/excluir credores.
3. **Cadastro de Contas a Pagar**: Formulário para adicionar/editar/excluir contas a pagar.
4. **Consultas e Relatórios**: Páginas para visualizar os diferentes relatórios e consultas disponíveis.

---

## Conclusão

Este sistema web fornece uma solução eficiente e escalável para o controle de contas a pagar de uma empresa, garantindo segurança, usabilidade e performance. As tecnologias escolhidas permitem uma arquitetura em múltiplas camadas, facilitando a manutenção e futura expansão do sistema.

LEMBRETES:

- MENSAGENS FLASH.
- RETORNOS DE TRATAMENTOS DE ERROS PERSONALIZADOS.
- ROTINAS DE LOGIN E LOGOUT.
- REGISTROS DE LOG.
- 
