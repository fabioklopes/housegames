function getCookie(nome) {
    const linha = document.cookie.split('; ').find((row) => row.startsWith(nome + '='));
    return linha ? decodeURIComponent(linha.split('=')[1]) : null;
}

const timerEl = document.getElementById('timer');
const pontosEl = document.getElementById('pontos-valor');
const fichasEl = document.getElementById('fichas-embaralhadas');
const tracosEl = document.getElementById('tracos');
const sombraEl = document.getElementById('sombra-efeito');
const listaResolvidasEl = document.getElementById('lista-resolvidas');
const areaPalavraEl = document.getElementById('area-palavra');
const entradaEl = document.getElementById('entrada-oculta');

let palavraAtual = PALAVRA_EMBARALHADA_INICIAL;
let letrasDigitadas = [];
let travado = false;
let jogoEncerrado = false;

const MAPA_SEM_ACENTO = {
    'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A',
    'É': 'E', 'Ê': 'E',
    'Í': 'I',
    'Ó': 'O', 'Ô': 'O', 'Õ': 'O',
    'Ú': 'U', 'Ü': 'U',
};

function normalizarCaractere(caractere) {
    const maiuscula = caractere.toUpperCase();
    if (maiuscula === 'Ç') return 'Ç';
    return MAPA_SEM_ACENTO[maiuscula] || maiuscula;
}

function indicesDeLetras(palavra) {
    const indices = [];
    for (let i = 0; i < palavra.length; i += 1) {
        if (palavra[i] !== '-') indices.push(i);
    }
    return indices;
}

function renderFichas(palavra) {
    fichasEl.innerHTML = '';
    palavra.split('').forEach((caractere) => {
        const div = document.createElement('div');
        if (caractere === '-') {
            div.className = 'ficha-hifen';
            div.textContent = '-';
        } else {
            div.className = 'ficha';
            div.textContent = caractere;
        }
        fichasEl.appendChild(div);
    });
}

function renderTracos(palavra, digitadas) {
    tracosEl.innerHTML = '';
    let cursor = 0;
    palavra.split('').forEach((caractere) => {
        const div = document.createElement('div');
        if (caractere === '-') {
            div.className = 'traco-hifen';
            div.textContent = '-';
        } else {
            const letra = digitadas[cursor];
            const eAtual = letra === undefined;
            div.className = letra ? 'traco preenchido' : (eAtual ? 'traco atual' : 'traco');
            div.textContent = letra || '';
            cursor += 1;
        }
        tracosEl.appendChild(div);
    });
}

function focarEntrada() {
    if (!travado && !jogoEncerrado) entradaEl.focus({ preventScroll: true });
}

function iniciarPalavra(embaralhada) {
    palavraAtual = embaralhada;
    letrasDigitadas = [];
    entradaEl.value = '';
    renderFichas(palavraAtual);
    renderTracos(palavraAtual, letrasDigitadas);
    focarEntrada();
}

function dispararEfeito(classe) {
    sombraEl.classList.remove('efeito-acerto', 'efeito-erro');
    // força reflow para permitir reiniciar a mesma animação em sequência
    void sombraEl.offsetWidth;
    sombraEl.classList.add(classe);
}

// O foco num <input> real é o que dispara o teclado virtual em celulares —
// um listener de keydown na window (como numa versão anterior) só funciona
// com teclado físico. O input fica invisível sobre a área da palavra; o
// valor digitado nele é a fonte da verdade, normalizado a cada evento.
entradaEl.addEventListener('input', () => {
    if (travado || jogoEncerrado) {
        entradaEl.value = '';
        return;
    }

    const totalLetras = indicesDeLetras(palavraAtual).length;
    const normalizadas = entradaEl.value
        .split('')
        .map(normalizarCaractere)
        .filter((c) => /^[A-ZÇ]$/.test(c))
        .slice(0, totalLetras);

    letrasDigitadas = normalizadas;
    entradaEl.value = normalizadas.join('');
    renderTracos(palavraAtual, letrasDigitadas);

    if (letrasDigitadas.length === totalLetras) {
        enviarResposta();
    }
});

areaPalavraEl.addEventListener('click', focarEntrada);
entradaEl.addEventListener('blur', () => setTimeout(focarEntrada, 50));

async function enviarResposta() {
    travado = true;
    const digitada = letrasDigitadas.join('');
    try {
        const resp = await fetch(URL_VALIDAR, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ digitada }),
        });
        const dados = await resp.json();
        processarResultado(dados);
    } catch (erro) {
        travado = false;
    }
}

function processarResultado(dados) {
    if (typeof dados.pontos_rodada === 'number') {
        pontosEl.textContent = dados.pontos_rodada;
    }

    if (dados.tipo === 'correta') {
        dispararEfeito('efeito-acerto');
        const li = document.createElement('li');
        li.textContent = dados.palavra;
        listaResolvidasEl.insertBefore(li, listaResolvidasEl.firstChild);
        setTimeout(() => {
            if (dados.proxima_embaralhada) {
                iniciarPalavra(dados.proxima_embaralhada);
            }
            travado = false;
        }, 500);
    } else if (dados.tipo === 'errada') {
        dispararEfeito('efeito-erro');
        setTimeout(() => {
            letrasDigitadas = [];
            entradaEl.value = '';
            renderTracos(palavraAtual, letrasDigitadas);
            travado = false;
            focarEntrada();
        }, 500);
    } else if (dados.tipo === 'encerrada' || dados.tipo === 'sem_palavra') {
        jogoEncerrado = true;
        irParaResultado();
        return;
    } else {
        travado = false;
    }

    if (dados.rodada_encerrada) {
        jogoEncerrado = true;
        setTimeout(irParaResultado, 700);
    }
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
        `<div>${o.apelido}: ${o.acertos} acertos · ${o.pontos} pts${o.eliminado ? ' (eliminado)' : ''}</div>`
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

renderFichas(palavraAtual);
renderTracos(palavraAtual, letrasDigitadas);
atualizarTimerVisual();
focarEntrada();
setInterval(sincronizarEstado, 2500);
