import React, { useState, useEffect } from 'react';

function ContasAPagar() {
    const [contas, setContas] = useState([]);

    useEffect(() => {
        fetch('/api/contas')
            .then(response => response.json())
            .then(data => setContas(data));
    }, []);

    return (
        <div>
            <h2>Contas a Pagar</h2>
            <table>
                <thead>
                    <tr>
                        <th>Descrição</th>
                        <th>Valor</th>
                        <th>Data de Vencimento</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {contas.map(conta => (
                        <tr key={conta.id}>
                            <td>{conta.descricao}</td>
                            <td>{conta.valor}</td>
                            <td>{conta.data_vencimento}</td>
                            <td>{conta.status}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default ContasAPagar;
