import random
import unicodedata

from .palavras import BANCO_PALAVRAS

QTD_FILA_PADRAO = 30
MAX_TENTATIVAS_EMBARALHAR = 20


def normalizar_letra(caractere):
    """Maiusculiza e remove acentos, preservando a cedilha (Ç), que é
    exigida por ser uma letra fonética própria — diferente dos acentos
    gráficos (agudo, grave, til, circunflexo), que são ignorados."""
    maiuscula = caractere.upper()
    if maiuscula == 'Ç':
        return 'Ç'
    if maiuscula == '-':
        return '-'
    decomposta = unicodedata.normalize('NFD', maiuscula)
    return ''.join(c for c in decomposta if not unicodedata.combining(c))


def normalizar_palavra(texto):
    return ''.join(normalizar_letra(c) for c in texto)


def _embaralhar(palavra_normalizada):
    """Embaralha as letras da palavra mantendo os hífens fixos na posição
    original, para que palavras compostas continuem exibindo o hífen no
    lugar certo."""
    indices_letras = [i for i, c in enumerate(palavra_normalizada) if c != '-']
    letras = [palavra_normalizada[i] for i in indices_letras]

    if len(set(letras)) <= 1:
        return palavra_normalizada

    candidato = list(palavra_normalizada)
    for _ in range(MAX_TENTATIVAS_EMBARALHAR):
        valores = letras[:]
        random.shuffle(valores)
        candidato = list(palavra_normalizada)
        for indice, valor in zip(indices_letras, valores):
            candidato[indice] = valor
        if ''.join(candidato) != palavra_normalizada:
            break
    return ''.join(candidato)


def _montar_item(exibida):
    normalizada = normalizar_palavra(exibida)
    return {
        'resposta': normalizada.replace('-', ''),
        'exibida': exibida,
        'embaralhada': _embaralhar(normalizada),
    }


def gerar_fila(nivel, qtd=None):
    """Gera a fila de palavras (já embaralhadas) de uma rodada. Sorteia sem
    repetição até esgotar o banco do nível e, se precisar de mais, reinicia
    o ciclo embaralhado evitando repetir a última palavra imediatamente."""
    meta = qtd if qtd is not None else QTD_FILA_PADRAO
    candidatos = BANCO_PALAVRAS[nivel]

    fila = []
    pool = []
    while len(fila) < meta:
        if not pool:
            pool = candidatos[:]
            random.shuffle(pool)
            if fila and pool[-1] == fila[-1]['exibida']:
                pool.insert(0, pool.pop())
        exibida = pool.pop()
        fila.append(_montar_item(exibida))
    return fila


def validar_resposta(digitada, item):
    return normalizar_palavra(digitada) == item['resposta']


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

    Critério: 1) quem acertou mais palavras vence; 2) entre os que empatam,
    quem errou menos vence; 3) empate residual: sorteio determinístico pela
    seed da partida/fase (quem sobrar em último aqui joga o desempate).
    """
    rng = random.Random(seed)
    embaralhados = participantes_info[:]
    rng.shuffle(embaralhados)

    def chave(info):
        return (-info['acertos'], info['erros'])

    return sorted(embaralhados, key=chave)
