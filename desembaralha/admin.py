from django.contrib import admin

from .models import Participante, Partida, QuadroJogador, Rodada

admin.site.register(Partida)
admin.site.register(Participante)
admin.site.register(Rodada)
admin.site.register(QuadroJogador)
