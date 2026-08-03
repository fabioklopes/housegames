from django.contrib import admin
from django.db.models import F
from django.utils import timezone

from .models import PalavraParaAvaliacao, Participante, Partida, QuadroJogador, Rodada

admin.site.register(Partida)
admin.site.register(Participante)
admin.site.register(Rodada)
admin.site.register(QuadroJogador)


@admin.action(description='Aprovar e creditar +5 pontos ao jogador')
def aprovar_e_creditar(modeladmin, request, queryset):
    pendentes = queryset.filter(status=PalavraParaAvaliacao.Status.PENDENTE)
    for item in pendentes:
        Participante.objects.filter(id=item.participante_id).update(pontos_totais=F('pontos_totais') + 5)
    pendentes.update(status=PalavraParaAvaliacao.Status.APROVADA, avaliada_em=timezone.now())


@admin.action(description='Rejeitar')
def rejeitar(modeladmin, request, queryset):
    queryset.filter(status=PalavraParaAvaliacao.Status.PENDENTE).update(
        status=PalavraParaAvaliacao.Status.REJEITADA, avaliada_em=timezone.now(),
    )


@admin.register(PalavraParaAvaliacao)
class PalavraParaAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('palavra_ascii', 'participante', 'partida', 'status', 'criada_em')
    list_filter = ('status', 'partida')
    actions = [aprovar_e_creditar, rejeitar]
