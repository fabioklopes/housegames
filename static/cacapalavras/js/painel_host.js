async function atualizarPainel() {
    const resp = await fetch(URL_ESTADO_HOST);
    const dados = await resp.json();

    const statusEl = document.getElementById('status-fase');
    if (dados.status === 'finalizada') {
        statusEl.textContent = 'Partida finalizada';
    } else {
        let texto = `Fase ${dados.fase_atual} · Nível ${dados.nivel_atual}`;
        if (dados.desempate_em_andamento) {
            texto += ' · Desempate em andamento';
        }
        if (typeof dados.tempo_restante === 'number') {
            texto += ` · ${dados.tempo_restante}s restantes`;
        }
        statusEl.textContent = texto;
    }

    const corpo = document.getElementById('tabela-participantes');
    corpo.innerHTML = dados.participantes.map((p) => `
        <tr class="${p.eliminado ? 'linha-eliminado' : ''}">
            <td>${p.apelido}${p.eliminado ? ' 🚫' : ''}</td>
            <td>${p.encontradas !== null ? `${p.encontradas}/${p.total_palavras}` : '—'}</td>
            <td>${p.pontos_totais}</td>
            <td>${p.eliminado ? 'Eliminado' : 'Em jogo'}</td>
        </tr>
    `).join('');

    const banner = document.getElementById('banner-campeao');
    if (dados.campeao) {
        banner.style.display = 'block';
        banner.textContent = `🏆 Campeão: ${dados.campeao}`;
    }
}

atualizarPainel();
setInterval(atualizarPainel, 2000);
