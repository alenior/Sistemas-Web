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
