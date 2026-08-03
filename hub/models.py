from django.db import models


class Jogador(models.Model):
    apelido = models.CharField(max_length=30)
    session_key = models.CharField(max_length=40, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.apelido


class Trofeu(models.Model):
    class Modalidade(models.TextChoices):
        CACAPALAVRAS = 'cacapalavras', 'Caça-Palavras'
        DESEMBARALHA = 'desembaralha', 'Desembaralha'
        FORCA = 'forca', 'Forca'
        JOGODAVELHA = 'jogodavelha', 'Jogo da Velha'
        LIGMIX = 'ligmix', 'LigMix'
        MULTIPLEX = 'multiplex', 'Multiplex'
        PALAVRASCRUZADAS = 'palavrascruzadas', 'Palavras Cruzadas'
        SOMAMAIS = 'somamais', 'SomaMais'

    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE, related_name='trofeus')
    modalidade = models.CharField(max_length=20, choices=Modalidade.choices)
    conquistado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.jogador.apelido} - {self.get_modalidade_display()}'
