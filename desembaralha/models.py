import random
import string

from django.db import models

from hub.models import Jogador

NIVEIS = ['facil', 'medio', 'dificil']

PONTOS_NIVEL = {
    'facil': 5,
    'medio': 15,
    'dificil': 30,
}

DURACAO_NIVEL = {
    'facil': 120,
    'medio': 90,
    'dificil': 45,
}

DURACAO_DESEMPATE = 30


def gerar_codigo():
    alfabeto = string.ascii_uppercase + string.digits
    while True:
        codigo = ''.join(random.choices(alfabeto, k=6))
        if not Partida.objects.filter(codigo=codigo).exists():
            return codigo


class Partida(models.Model):
    class Status(models.TextChoices):
        AGUARDANDO = 'aguardando', 'Aguardando jogadores'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        FINALIZADA = 'finalizada', 'Finalizada'

    codigo = models.CharField(max_length=6, unique=True, default=gerar_codigo)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.AGUARDANDO)
    fase_atual = models.PositiveSmallIntegerField(default=0)
    nivel_atual = models.CharField(max_length=10, choices=[(n, n) for n in NIVEIS], default='facil')
    max_jogadores = models.PositiveSmallIntegerField(default=8)
    host_session_key = models.CharField(max_length=40)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Partida {self.codigo}'

    def participantes_ativos(self):
        return self.participantes.filter(eliminado=False)

    def rodada_atual(self):
        return self.rodadas.order_by('-fase', '-sequencia').first()


class Participante(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='participantes')
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE, related_name='participacoes_desembaralha')
    eliminado = models.BooleanField(default=False)
    pontos_totais = models.PositiveIntegerField(default=0)
    ordem_eliminacao = models.PositiveSmallIntegerField(null=True, blank=True)
    entrou_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('partida', 'jogador')

    def __str__(self):
        return f'{self.jogador.apelido} em {self.partida.codigo}'


class Rodada(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='rodadas')
    fase = models.PositiveSmallIntegerField()
    sequencia = models.PositiveSmallIntegerField(default=0)
    nivel = models.CharField(max_length=10, choices=[(n, n) for n in NIVEIS])
    duracao_segundos = models.PositiveSmallIntegerField()
    desempate = models.BooleanField(default=False)
    iniciada_em = models.DateTimeField(auto_now_add=True)
    encerrada = models.BooleanField(default=False)

    class Meta:
        unique_together = ('partida', 'fase', 'sequencia')
        ordering = ['fase', 'sequencia']

    def __str__(self):
        sufixo = ' (desempate)' if self.desempate else ''
        return f'Rodada {self.fase}{sufixo} ({self.nivel}) - {self.partida.codigo}'

    def tempo_restante(self):
        from django.utils import timezone
        decorrido = (timezone.now() - self.iniciada_em).total_seconds()
        return max(0, self.duracao_segundos - int(decorrido))


class QuadroJogador(models.Model):
    """Painel individual de um participante numa rodada.

    `fila_palavras` guarda a sequência de palavras (com a forma embaralhada
    já sorteada e fixa) que serão apresentadas ao jogador; `indice_atual`
    aponta para a palavra corrente. Diferente do Caça-Palavras, a fila é um
    fluxo contínuo — a rodada nunca "termina" por completar a lista, só pelo
    tempo (exceto no desempate, que tem uma única palavra).
    """
    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE, related_name='quadros')
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='quadros')
    fila_palavras = models.JSONField()
    indice_atual = models.PositiveSmallIntegerField(default=0)
    resolvidas = models.JSONField(default=list, blank=True)
    pontos_rodada = models.PositiveIntegerField(default=0)
    acertos = models.PositiveSmallIntegerField(default=0)
    erros = models.PositiveSmallIntegerField(default=0)
    terminou_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('rodada', 'participante')

    def __str__(self):
        return f'Quadro de {self.participante.jogador.apelido} - fase {self.rodada.fase}'

    def palavra_atual(self):
        if self.indice_atual < len(self.fila_palavras):
            return self.fila_palavras[self.indice_atual]
        return None

    def completou(self):
        """Só se aplica ao desempate (fila de 1 palavra) — numa rodada normal
        a fila é longa o bastante para nunca se esgotar dentro do tempo."""
        return self.rodada.desempate and self.indice_atual >= len(self.fila_palavras)
