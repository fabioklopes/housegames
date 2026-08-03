function getCookie(nome) {
    const linha = document.cookie.split('; ').find((row) => row.startsWith(nome + '='));
    return linha ? decodeURIComponent(linha.split('=')[1]) : null;
}

const grid = document.getElementById('grid');
const timerEl = document.getElementById('timer');
const pontosEl = document.getElementById('pontos-valor');

let arrastando = false;
let inicio = null;
let caminhoAtual = [];
let jogoEncerrado = false;

function celulaDe(r, c) {
    return grid.querySelector(`.celula[data-r="${r}"][data-c="${c}"]`);
}

function celulaSobPonteiro(x, y) {
    const el = document.elementFromPoint(x, y);
    return el && el.classList.contains('celula') ? el : null;
}

function limparSelecaoVisual() {
    grid.querySelectorAll('.celula.selecionando').forEach((el) => el.classList.remove('selecionando'));
}

function calcularCaminho(a, b) {
    const dr = Math.sign(b.r - a.r);
    const dc = Math.sign(b.c - a.c);
    if (dr === 0 && dc === 0) return [a];
    const distR = Math.abs(b.r - a.r);
    const distC = Math.abs(b.c - a.c);
    if (dr !== 0 && dc !== 0 && distR !== distC) return null;
    const passos = Math.max(distR, distC);
    const caminho = [];
    for (let i = 0; i <= passos; i += 1) {
        caminho.push({ r: a.r + dr * i, c: a.c + dc * i });
    }
    return caminho;
}

function aplicarSelecaoVisual(caminho) {
    limparSelecaoVisual();
    caminho.forEach(({ r, c }) => {
        const el = celulaDe(r, c);
        if (el) el.classList.add('selecionando');
    });
}

grid.addEventListener('pointerdown', (ev) => {
    if (jogoEncerrado) return;
    const el = ev.target.closest('.celula');
    if (!el) return;
    arrastando = true;
    inicio = { r: parseInt(el.dataset.r, 10), c: parseInt(el.dataset.c, 10) };
    caminhoAtual = [inicio];
    aplicarSelecaoVisual(caminhoAtual);
    ev.preventDefault();
});

window.addEventListener('pointermove', (ev) => {
    if (!arrastando) return;
    const el = celulaSobPonteiro(ev.clientX, ev.clientY);
    if (!el) return;
    const atual = { r: parseInt(el.dataset.r, 10), c: parseInt(el.dataset.c, 10) };
    const caminho = calcularCaminho(inicio, atual);
    if (caminho) {
        caminhoAtual = caminho;
        aplicarSelecaoVisual(caminho);
    }
});

window.addEventListener('pointerup', () => {
    if (!arrastando) return;
    arrastando = false;
    if (caminhoAtual.length >= 2) {
        enviarSelecao(caminhoAtual);
    } else {
        limparSelecaoVisual();
    }
});

async function enviarSelecao(caminho) {
    const celulas = caminho.map((p) => [p.r, p.c]);
    const resp = await fetch(URL_VALIDAR, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ celulas }),
    });
    const dados = await resp.json();
    processarResultado(dados, caminho);
}

function processarResultado(dados, caminho) {
    if (typeof dados.pontos_rodada === 'number') {
        pontosEl.textContent = dados.pontos_rodada;
    }

    if (dados.tipo === 'lista') {
        pintarCelulas(caminho, dados.cor);
        marcarPalavraEncontrada(dados.palavra);
        limparSelecaoVisual();
    } else if (dados.tipo === 'bonus') {
        pintarCelulas(caminho, 'rgba(255,255,255,0.55)');
        limparSelecaoVisual();
    } else if (dados.tipo === 'invalida') {
        piscarInvalida(caminho);
    } else if (dados.tipo === 'encerrada') {
        irParaResultado();
        return;
    } else {
        limparSelecaoVisual();
    }

    if (dados.rodada_encerrada) {
        jogoEncerrado = true;
        setTimeout(irParaResultado, 900);
    }
}

function pintarCelulas(caminho, cor) {
    caminho.forEach(({ r, c }) => {
        const el = celulaDe(r, c);
        if (el) {
            el.style.background = cor;
            el.style.color = '#1a1a1a';
        }
    });
}

function marcarPalavraEncontrada(palavraExibida) {
    const li = Array.from(document.querySelectorAll('#lista-palavras li'))
        .find((item) => item.dataset.palavra === palavraExibida);
    if (li) li.classList.add('encontrada');
}

function piscarInvalida(caminho) {
    const elementos = caminho.map(({ r, c }) => celulaDe(r, c)).filter(Boolean);
    elementos.forEach((el) => el.classList.add('piscar-invalida'));
    setTimeout(() => {
        elementos.forEach((el) => el.classList.remove('piscar-invalida'));
        limparSelecaoVisual();
    }, 650);
}

function atualizarTimerVisual() {
    timerEl.textContent = TEMPO_RESTANTE;
    timerEl.classList.remove('timer-alerta', 'timer-zero');
    if (TEMPO_RESTANTE <= 0) {
        timerEl.classList.add('timer-zero');
    } else if (TEMPO_RESTANTE <= 10) {
        timerEl.classList.add('timer-alerta');
    }
}

function irParaResultado() {
    window.location.href = URL_RESULTADO;
}

function atualizarOponentes(oponentes) {
    const container = document.getElementById('oponentes');
    if (!oponentes.length) {
        container.innerHTML = '';
        return;
    }
    container.innerHTML = '<h4>Oponentes</h4>' + oponentes.map((o) => (
        `<div>${o.apelido}: ${o.progresso}/${o.total} palavras · ${o.pontos} pts${o.eliminado ? ' (eliminado)' : ''}</div>`
    )).join('');
}

async function sincronizarEstado() {
    if (jogoEncerrado) return;
    try {
        const resp = await fetch(URL_ESTADO);
        const dados = await resp.json();
        if (typeof dados.tempo_restante === 'number') {
            TEMPO_RESTANTE = dados.tempo_restante;
            atualizarTimerVisual();
        }
        atualizarOponentes(dados.oponentes || []);
        if (dados.encerrada) {
            jogoEncerrado = true;
            irParaResultado();
        }
    } catch (erro) {
        /* falha temporária de rede: tenta novamente no próximo ciclo */
    }
}

setInterval(() => {
    if (jogoEncerrado) return;
    TEMPO_RESTANTE = Math.max(0, TEMPO_RESTANTE - 1);
    atualizarTimerVisual();
    if (TEMPO_RESTANTE <= 0) {
        jogoEncerrado = true;
        setTimeout(irParaResultado, 500);
    }
}, 1000);

atualizarTimerVisual();
setInterval(sincronizarEstado, 2500);
