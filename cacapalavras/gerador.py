import random

from .palavras import BANCO_PALAVRAS, banco_completo

CANDY_PALETTE = [
    '#FF6F91', '#FFC75F', '#845EC2', '#00C2A8',
    '#FF9671', '#F9F871', '#0089BA', '#D65DB1',
    '#FF8066', '#4FFBDF',
]

CONFIG_NIVEL = {
    'facil': {
        'tamanho': 10,
        'qtd_palavras': 6,
        'direcoes': [(0, 1), (1, 0)],
    },
    'medio': {
        'tamanho': 12,
        'qtd_palavras': 8,
        'direcoes': [(0, 1), (1, 0), (1, 1), (1, -1)],
    },
    'dificil': {
        'tamanho': 14,
        'qtd_palavras': 10,
        'direcoes': [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1),
        ],
    },
}

LETRAS_FREQUENTES = list(
    'AAAAAAAAEEEEEEEEIIIIOOOOOOUUUBCDDFGHJLLMNNPPQRRRSSSSTTTVXZ'
)

MAX_TENTATIVAS_POR_PALAVRA = 60


def _cabe_no_grid(grid, tamanho, palavra, linha, coluna, d_lin, d_col):
    celulas = []
    for i, letra in enumerate(palavra):
        r = linha + d_lin * i
        c = coluna + d_col * i
        if not (0 <= r < tamanho and 0 <= c < tamanho):
            return None
        atual = grid[r][c]
        if atual is not None and atual != letra:
            return None
        celulas.append((r, c))
    return celulas


def _posicionar_palavra(grid, tamanho, palavra, direcoes):
    direcoes_embaralhadas = direcoes[:]
    random.shuffle(direcoes_embaralhadas)
    for _ in range(MAX_TENTATIVAS_POR_PALAVRA):
        d_lin, d_col = random.choice(direcoes_embaralhadas)
        linha = random.randrange(tamanho)
        coluna = random.randrange(tamanho)
        celulas = _cabe_no_grid(grid, tamanho, palavra, linha, coluna, d_lin, d_col)
        if celulas is not None:
            for (r, c), letra in zip(celulas, palavra):
                grid[r][c] = letra
            return celulas
    return None


def gerar_quadro(nivel, qtd_palavras=None):
    """Gera um tabuleiro individual (grid + palavras posicionadas) para um nível.

    `qtd_palavras`, quando informado, sobrepõe a quantidade padrão do nível
    (usado pela rodada de desempate, que tem uma única palavra).
    """
    config = CONFIG_NIVEL[nivel]
    tamanho = config['tamanho']
    meta_palavras = qtd_palavras if qtd_palavras is not None else config['qtd_palavras']
    candidatos = [item for item in BANCO_PALAVRAS[nivel] if len(item[0]) <= tamanho]
    random.shuffle(candidatos)

    grid = [[None] * tamanho for _ in range(tamanho)]
    palavras_colocadas = []
    for ascii_form, exibida in candidatos:
        if len(palavras_colocadas) >= meta_palavras:
            break
        celulas = _posicionar_palavra(grid, tamanho, ascii_form, config['direcoes'])
        if celulas is not None:
            cor = CANDY_PALETTE[len(palavras_colocadas) % len(CANDY_PALETTE)]
            palavras_colocadas.append({
                'palavra': ascii_form,
                'exibida': exibida,
                'celulas': [list(c) for c in celulas],
                'cor': cor,
                'encontrada': False,
            })

    for r in range(tamanho):
        for c in range(tamanho):
            if grid[r][c] is None:
                grid[r][c] = random.choice(LETRAS_FREQUENTES)

    return grid, palavras_colocadas


def _celulas_em_linha_reta(celulas):
    if len(celulas) < 2:
        return False
    (r0, c0), (r1, c1) = celulas[0], celulas[1]
    d_lin = r1 - r0
    d_col = c1 - c0
    if d_lin == 0 and d_col == 0:
        return False
    passo_lin = (d_lin > 0) - (d_lin < 0)
    passo_col = (d_col > 0) - (d_col < 0)
    if d_lin != 0 and d_col != 0 and abs(d_lin) != abs(d_col):
        return False
    for i, (r, c) in enumerate(celulas):
        if r != r0 + passo_lin * i or c != c0 + passo_col * i:
            return False
    return True


def validar_selecao(celulas, grid, lista_palavras, bonus_encontrados):
    """Valida a seleção de células feita pelo jogador no seu próprio quadro.

    Retorna um dict {tipo: 'lista' | 'bonus' | 'invalida', ...}.
    """
    if not _celulas_em_linha_reta(celulas):
        return {'tipo': 'invalida'}

    palavra_formada = ''.join(grid[r][c] for r, c in celulas)
    palavra_invertida = palavra_formada[::-1]

    for item in lista_palavras:
        if item['encontrada']:
            continue
        celulas_item = [tuple(c) for c in item['celulas']]
        if celulas_item == celulas or celulas_item == list(reversed(celulas)):
            item['encontrada'] = True
            return {
                'tipo': 'lista',
                'palavra': item['exibida'],
                'cor': item['cor'],
                'celulas': item['celulas'],
            }

    banco = banco_completo()
    # Lista de listas (não tuplas): bonus_encontrados é persistido em JSONField,
    # que não tem tipo tupla, então a comparação precisa usar a mesma forma
    # antes e depois do round-trip pelo banco de dados.
    span = [list(c) for c in sorted(celulas)]
    if span in bonus_encontrados:
        return {'tipo': 'invalida'}

    if palavra_formada in banco or palavra_invertida in banco:
        exibida = banco.get(palavra_formada) or banco.get(palavra_invertida)
        bonus_encontrados.append(span)
        return {
            'tipo': 'bonus',
            'palavra': exibida,
            'celulas': [list(c) for c in celulas],
        }

    # Linha reta válida, mas a palavra formada não é reconhecida (nem da
    # lista, nem do banco curado): fica marcada para o caller registrar como
    # pendência de avaliação, sem pontuar por enquanto.
    return {
        'tipo': 'invalida',
        'linha_reta': True,
        'palavra_formada': palavra_formada,
        'celulas': [list(c) for c in celulas],
    }


def proximo_nivel(nivel_atual):
    ordem = ['facil', 'medio', 'dificil']
    if nivel_atual not in ordem:
        return 'dificil'
    indice = ordem.index(nivel_atual)
    if indice + 1 < len(ordem):
        return ordem[indice + 1]
    return 'dificil'


def ordenar_por_desempenho(participantes_info, seed):
    """Ordena participantes do melhor para o pior desempenho na rodada.

    participantes_info: lista de dicts {participante_id, encontradas, completou, terminou_em}
    Critério: 1) quem localizou mais palavras da própria lista vence;
    2) entre os que empatam, quem terminou mais rápido (terminou_em menor) vence;
    3) empate residual: sorteio determinístico pela seed da partida/fase
    (quem sobrar em último aqui joga a rodada de desempate de 1 palavra).
    """
    rng = random.Random(seed)
    embaralhados = participantes_info[:]
    rng.shuffle(embaralhados)

    def chave(info):
        terminou_em = info['terminou_em']
        ordem_tempo = terminou_em.timestamp() if terminou_em else float('inf')
        return (-info['encontradas'], ordem_tempo)

    return sorted(embaralhados, key=chave)
