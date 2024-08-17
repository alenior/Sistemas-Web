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
            <h2>Credores</h2>
            <ul>
                {credores.map(credor => (
                    <li key={credor.id}>
                        {credor.nome} 
                        <button>Editar</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Credores;
