from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render

from .models import Jogador, Trofeu


def index(request):
    jogos_disponiveis = [
        {'nome': 'Caça-Palavras', 'slug': 'cacapalavras', 'url': 'cacapalavras_criar'},
    ]
    return render(request, 'hub/index.html', {'jogos_disponiveis': jogos_disponiveis})


def ranking(request):
    linhas = (
        Jogador.objects
        .annotate(pontos_cacapalavras=Coalesce(Sum('participacoes_cacapalavras__pontos_totais'), 0))
        .order_by('-pontos_cacapalavras')
    )
    for linha in linhas:
        linha.pontos_total = linha.pontos_cacapalavras
    return render(request, 'hub/ranking.html', {'linhas': linhas})


def reiniciar_sessao(request):
    if request.method == 'POST':
        from cacapalavras.models import Participante
        Participante.objects.update(pontos_totais=0)
        return redirect('hub_index')
    return render(request, 'hub/confirmar.html', {
        'titulo': 'Reiniciar a seção dos jogadores',
        'mensagem': 'Isso zera a pontuação de todos os jogadores em todas as modalidades. '
                    'Os jogadores continuam cadastrados. Tem certeza?',
    })


def nova_secao(request):
    if request.method == 'POST':
        from cacapalavras.models import Partida
        Partida.objects.all().delete()
        Jogador.objects.all().delete()
        return redirect('hub_index')
    return render(request, 'hub/confirmar.html', {
        'titulo': 'Iniciar uma nova seção',
        'mensagem': 'Isso apaga todos os jogadores e partidas em andamento — todos precisarão se '
                    'cadastrar de novo. Tem certeza?',
    })
