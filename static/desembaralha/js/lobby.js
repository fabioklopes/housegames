function getCookie(nome) {
    const linha = document.cookie.split('; ').find((row) => row.startsWith(nome + '='));
    return linha ? decodeURIComponent(linha.split('=')[1]) : null;
}

async function atualizarStatus() {
    const resp = await fetch(URL_STATUS);
    const dados = await resp.json();

    document.getElementById('total-jogadores').textContent = dados.total;
    const lista = document.getElementById('lista-jogadores');
    lista.innerHTML = '';
    dados.participantes.forEach((apelido) => {
        const li = document.createElement('li');
        li.textContent = apelido;
        lista.appendChild(li);
    });

    if (E_HOST) {
        document.getElementById('btn-iniciar').disabled = dados.total < 2;
    }

    if (dados.status !== 'aguardando') {
        window.location.href = URL_DESTINO;
    }
}

if (E_HOST) {
    document.getElementById('btn-iniciar').addEventListener('click', async () => {
        const resp = await fetch(URL_INICIAR, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });
        const dados = await resp.json();
        if (!dados.ok) {
            document.getElementById('msg-iniciar').textContent = dados.erro;
        }
    });
}

atualizarStatus();
setInterval(atualizarStatus, 2000);
