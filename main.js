const NODES = ['http://localhost:5000', 'http://localhost:5001', 'http://localhost:5002'];


async function startNetwork() {
    for (let node of NODES) {
        let others = NODES.filter(n => n !== node);
        try { await fetch(`${node}/nodes/register`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({nodes: others}) }); } catch(e){}
    }
    try {
        await fetch(`${NODES[0]}/transactions/new`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sender: "GENESIS", recipient: "REDE", amount: 0, content: "ROOT"}) });
        await fetch(`${NODES[0]}/mine`);
        await runConsensus();
        alert("Rede Iniciada!");
        loadChain();
    } catch(e) { alert("Erro ao iniciar. Verifique os terminais."); }
}

async function runConsensus() {
    for (let node of NODES) { try { await fetch(`${node}/nodes/resolve`); } catch(e){} }
}

async function mineBlock() {
    const node = document.getElementById('txNode').value;
    const sender = document.getElementById('sender').value.trim();
    const recipient = document.getElementById('recipient').value.trim();
    const amount = document.getElementById('amount').value;
    const content = document.getElementById('content').value;

    try {
        document.body.style.cursor = 'wait';

        if (sender && recipient) {
            const body = { sender, recipient, amount: Number(amount), content };
            const resTx = await fetch(`${node}/transactions/new`, { 
                method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) 
            });
            if(!resTx.ok) throw new Error("Erro ao criar transação.");
        }

        const resMine = await fetch(`${node}/mine`);
        if(!resMine.ok) throw new Error("Falha na mineração");
        
        await runConsensus();
        
        document.body.style.cursor = 'default';
        alert(`Sucesso! Bloco Minerado.`);
        
        document.getElementById('sender').value = "";
        document.getElementById('recipient').value = "";
        document.getElementById('content').value = "";
        loadChain();

    } catch(e) { 
        document.body.style.cursor = 'default';
        alert(`Erro: ${e}`); 
    }
}

async function loadChain() {
    const node = document.getElementById('viewNode').value;
    const container = document.getElementById('chainContainer');
    container.innerHTML = "<p style='text-align:center; color:#888'>Carregando JSON</p>";
    
    try {
        const res = await fetch(`${node}/chain`);
        const data = await res.json();
        const chain = data.chain;
        
        container.innerHTML = "";
        
        if(chain.length === 0) { container.innerHTML = "Sem dados."; return; }

        for (let i = chain.length - 1; i >= 0; i--) {
            const block = chain[i];
        
            const currentHash = block.hash || "Hash não disponível";
            const cleanTransactions = block.transactions.map(tx => {
                const { content, ...rest } = tx; 
                return rest;
            });

            const html = `
                <div class="block-card">
                    <div class="block-header">
                        <span>BLOCO #${block.index}</span>
                    </div>
                    
                    <div style="margin-bottom:15px; font-size:0.9em">
                        <strong>Nonce:</strong> ${block.proof}
                    </div>

                    <div class="tx-area" style="margin-bottom: 20px;">
                        <strong>Transações (${block.transactions.length}):</strong>
                        <pre style="margin:10px 0 0 0; font-size:0.85em; overflow-x:auto; color:#444;">${JSON.stringify(cleanTransactions, null, 2)}</pre>
                    </div>
                    
                    <div class="hash-row">
                        <div class="hash-label">Prévio: </div>
                        <div class="hash-val">${block.previous_hash}</div>
                    </div>

                    <div class="hash-row">
                        <div class="hash-label">Hash: </div>
                        <div class="hash-val">${currentHash}</div>
                    </div>
                </div>
            `;

            container.innerHTML += html;
        }
    } catch(e) {
        container.innerHTML = `<p style="color:red; text-align:center">Erro ao conectar com ${node}</p>`;
    }
}

// Tabs
function openTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
    if(tabId === 'view') loadChain();
}

// Verifica a cada 10 segundos a consistência da rede
setInterval(() => { runConsensus(); }, 10000);