import React from 'react';
import Credores from './Credores';
import ContasAPagar from './ContasAPagar';

function App() {
    return (
        <div className="container">
            <h1>Sistema de Controle de Contas a Pagar</h1>
            <Credores />
            <ContasAPagar />
        </div>
    );
}

export default App;
