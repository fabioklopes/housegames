import io
import json

import qrcode
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from hub.models import Trofeu
from hub.utils import criar_ou_atualizar_jogador, obter_jogador_sessao

from . import gerador
from .models import (
    DURACAO_DESEMPATE,
    DURACAO_NIVEL,
    PONTOS_NIVEL,
    Participante,
    Partida,
    QuadroJogador,
    Rodada,
)


def criar_partida(request):
    if request.method == 'POST':
        try:
            max_jogadores = int(request.POST.get('max_jogadores', 8))
        except ValueError:
            max_jogadores = 8
        max_jogadores = max(2, min(8, max_jogadores))

        if not request.session.session_key:
            request.session.save()

        partida = Partida.objects.create(
            max_jogadores=max_jogadores,
            host_session_key=request.session.session_key,
        )
        return redirect('desembaralha_lobby', codigo=partida.codigo)

    return render(request, 'desembaralha/criar.html')


def _eh_host(request, partida):
    return bool(request.session.session_key) and request.session.session_key == partida.host_session_key


def lobby(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    if partida.status != Partida.Status.AGUARDANDO:
        return redirect('desembaralha_jogo', codigo=codigo)

    e_host = _eh_host(request, partida)
    return render(request, 'desembaralha/lobby.html', {
        'partida': partida,
        'e_host': e_host,
    })


def lobby_status(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    participantes = list(
        partida.participantes.select_related('jogador').values_list('jogador__apelido', flat=True)
    )
    return JsonResponse({
        'status': partida.status,
        'participantes': participantes,
        'total': len(participantes),
        'max_jogadores': partida.max_jogadores,
    })


def qrcode_imagem(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    url_entrada = request.build_absolute_uri(reverse('desembaralha_entrar', args=[partida.codigo]))
    img = qrcode.make(url_entrada)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def entrar(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)

    if partida.status != Partida.Status.AGUARDANDO:
        return render(request, 'desembaralha/entrar.html', {
            'partida': partida,
            'erro': 'Esta partida já começou.',
        })

    if request.method == 'POST':
        apelido = request.POST.get('apelido', '').strip()
        if not apelido:
            return render(request, 'desembaralha/entrar.html', {
                'partida': partida, 'erro': 'Informe um apelido.',
            })

        if partida.participantes.count() >= partida.max_jogadores:
            return render(request, 'desembaralha/entrar.html', {
                'partida': partida, 'erro': 'A partida já atingiu o número máximo de jogadores.',
            })

        jogador = criar_ou_atualizar_jogador(request, apelido)
        Participante.objects.get_or_create(partida=partida, jogador=jogador)
        return redirect('desembaralha_lobby', codigo=partida.codigo)

    return render(request, 'desembaralha/entrar.html', {'partida': partida})


def iniciar_partida(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    if request.method != 'POST' or not _eh_host(request, partida):
        return JsonResponse({'ok': False, 'erro': 'Não autorizado.'}, status=403)

    if partida.participantes.count() < 2:
        return JsonResponse({'ok': False, 'erro': 'É preciso pelo menos 2 jogadores.'}, status=400)

    _criar_rodada(partida, fase=1, sequencia=0, nivel='facil')
    partida.status = Partida.Status.EM_ANDAMENTO
    partida.fase_atual = 1
    partida.nivel_atual = 'facil'
    partida.save()
    return JsonResponse({'ok': True})


def _criar_rodada(partida, fase, sequencia, nivel, qtd_palavras=None, duracao=None,
                   desempate=False, participantes=None):
    rodada = Rodada.objects.create(
        partida=partida,
        fase=fase,
        sequencia=sequencia,
        nivel=nivel,
        duracao_segundos=duracao if duracao is not None else DURACAO_NIVEL[nivel],
        desempate=desempate,
    )
    alvo = participantes if participantes is not None else partida.participantes_ativos()
    for participante in alvo:
        fila = gerador.gerar_fila(nivel, qtd=qtd_palavras)
        QuadroJogador.objects.create(
            rodada=rodada,
            participante=participante,
            fila_palavras=fila,
        )
    return rodada


def _criar_rodada_desempate(rodada_anterior, participantes):
    partida = rodada_anterior.partida
    return _criar_rodada(
        partida,
        fase=rodada_anterior.fase,
        sequencia=rodada_anterior.sequencia + 1,
        nivel=rodada_anterior.nivel,
        qtd_palavras=1,
        duracao=DURACAO_DESEMPATE,
        desempate=True,
        participantes=participantes,
    )


def _participante_da_sessao(request, partida):
    jogador = obter_jogador_sessao(request)
    if jogador is None:
        return None
    return partida.participantes.filter(jogador=jogador).first()


def _verificar_fim_por_tempo(rodada):
    if not rodada.encerrada and rodada.tempo_restante() <= 0:
        _finalizar_rodada(rodada)


def _finalizar_rodada(rodada):
    if rodada.encerrada:
        return
    rodada.encerrada = True
    rodada.save(update_fields=['encerrada'])

    partida = rodada.partida
    info = []
    for quadro in rodada.quadros.select_related('participante__jogador'):
        participante = quadro.participante
        participante.pontos_totais += quadro.pontos_rodada
        participante.save(update_fields=['pontos_totais'])

        info.append({
            'participante_id': participante.id,
            'acertos': quadro.acertos,
            'erros': quadro.erros,
        })

    seed = f'{partida.codigo}-{rodada.fase}-{rodada.sequencia}'
    classificacao = gerador.ordenar_por_desempenho(info, seed=seed)
    pior_valor = classificacao[-1]['acertos']
    piores = [item for item in classificacao if item['acertos'] == pior_valor]

    if len(piores) > 1 and not rodada.desempate:
        # Empate no último lugar: disputa uma rodada extra de 1 palavra só
        # entre os empatados, sem eliminar ninguém ainda.
        ids_empatados = [item['participante_id'] for item in piores]
        participantes_empatados = Participante.objects.filter(id__in=ids_empatados)
        _criar_rodada_desempate(rodada, participantes_empatados)
        return

    pior = classificacao[-1]
    ja_eliminados = partida.participantes.filter(eliminado=True).count()
    participante_eliminado = Participante.objects.get(id=pior['participante_id'])
    participante_eliminado.eliminado = True
    participante_eliminado.ordem_eliminacao = ja_eliminados + 1
    participante_eliminado.save(update_fields=['eliminado', 'ordem_eliminacao'])

    restantes = partida.participantes_ativos().count()
    if restantes <= 1:
        partida.status = Partida.Status.FINALIZADA
        partida.save(update_fields=['status'])
        campeao = partida.participantes_ativos().first()
        if campeao is not None:
            Trofeu.objects.get_or_create(
                jogador=campeao.jogador,
                modalidade=Trofeu.Modalidade.DESEMBARALHA,
            )
    else:
        proximo_nivel = gerador.proximo_nivel(partida.nivel_atual)
        partida.fase_atual += 1
        partida.nivel_atual = proximo_nivel
        partida.save(update_fields=['fase_atual', 'nivel_atual'])
        _criar_rodada(partida, fase=partida.fase_atual, sequencia=0, nivel=proximo_nivel)


def jogo(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    participante = _participante_da_sessao(request, partida)
    if participante is None:
        if _eh_host(request, partida):
            return redirect('desembaralha_painel_host', codigo=codigo)
        return redirect('desembaralha_entrar', codigo=codigo)

    rodada = partida.rodada_atual()
    if rodada is None:
        return redirect('desembaralha_lobby', codigo=codigo)

    _verificar_fim_por_tempo(rodada)
    # A finalização acima pode ter encerrado a partida ou criado a próxima
    # rodada (normal ou de desempate) — busca de novo para refletir isso.
    partida.refresh_from_db()
    rodada = partida.rodada_atual()

    if partida.status == Partida.Status.FINALIZADA:
        return redirect('desembaralha_campeao', codigo=codigo)

    if participante.eliminado:
        return redirect('desembaralha_resultado', codigo=codigo)

    quadro = QuadroJogador.objects.filter(rodada=rodada, participante=participante).first()
    if quadro is None:
        # Participante não está entre os empatados numa rodada de desempate:
        # aguarda o desfecho sem ser redirecionado para o resultado da fase.
        return render(request, 'desembaralha/aguardando.html', {'partida': partida})

    if rodada.encerrada:
        return redirect('desembaralha_resultado', codigo=codigo)

    palavra_atual = quadro.palavra_atual()
    return render(request, 'desembaralha/jogo.html', {
        'partida': partida,
        'rodada': rodada,
        'quadro': quadro,
        'palavra_embaralhada': palavra_atual['embaralhada'] if palavra_atual else '',
        'resolvidas': quadro.resolvidas,
        'tempo_total': rodada.duracao_segundos,
        'tempo_restante': rodada.tempo_restante(),
    })


def estado_jogo(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    participante = _participante_da_sessao(request, partida)
    if participante is None:
        return JsonResponse({'erro': 'Jogador não encontrado nesta partida.'}, status=404)

    rodada = partida.rodada_atual()
    if rodada is None:
        return JsonResponse({'aguardando': True})

    _verificar_fim_por_tempo(rodada)

    quadro = QuadroJogador.objects.filter(rodada=rodada, participante=participante).first()
    oponentes = []
    for outro in rodada.quadros.select_related('participante__jogador').exclude(participante=participante):
        oponentes.append({
            'apelido': outro.participante.jogador.apelido,
            'acertos': outro.acertos,
            'pontos': outro.pontos_rodada,
            'eliminado': outro.participante.eliminado,
        })

    return JsonResponse({
        'encerrada': rodada.encerrada,
        'tempo_restante': rodada.tempo_restante(),
        'pontos_rodada': quadro.pontos_rodada if quadro else 0,
        'eliminado': participante.eliminado,
        'oponentes': oponentes,
    })


def validar_palavra(request, codigo):
    if request.method != 'POST':
        return JsonResponse({'tipo': 'invalida'}, status=405)

    partida = get_object_or_404(Partida, codigo=codigo)
    participante = _participante_da_sessao(request, partida)
    if participante is None:
        return JsonResponse({'erro': 'Jogador não encontrado nesta partida.'}, status=404)

    rodada = partida.rodada_atual()
    if rodada is None or rodada.encerrada:
        return JsonResponse({'tipo': 'encerrada'})

    try:
        dados = json.loads(request.body)
        digitada = str(dados.get('digitada', ''))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'tipo': 'invalida'})

    quadro = get_object_or_404(QuadroJogador, rodada=rodada, participante=participante)
    item = quadro.palavra_atual()
    if item is None:
        return JsonResponse({'tipo': 'sem_palavra'})

    if gerador.validar_resposta(digitada, item):
        quadro.acertos += 1
        quadro.pontos_rodada += PONTOS_NIVEL[rodada.nivel]
        quadro.resolvidas.append(item['exibida'])
        quadro.indice_atual += 1
        quadro.save()

        proxima = quadro.palavra_atual()
        resultado = {
            'tipo': 'correta',
            'palavra': item['exibida'],
            'pontos_rodada': quadro.pontos_rodada,
            'proxima_embaralhada': proxima['embaralhada'] if proxima else None,
        }
    else:
        quadro.erros += 1
        quadro.save(update_fields=['erros'])
        resultado = {'tipo': 'errada', 'pontos_rodada': quadro.pontos_rodada}

    round_finalizada_agora = quadro.completou() and rodada.tempo_restante() > 0
    if round_finalizada_agora:
        _finalizar_rodada(rodada)
        quadro.refresh_from_db()

    resultado['rodada_encerrada'] = rodada.encerrada
    return JsonResponse(resultado)


def resultado_fase(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    participante = _participante_da_sessao(request, partida)
    if participante is None:
        return redirect('desembaralha_entrar', codigo=codigo)

    rodada = partida.rodada_atual()
    if rodada is None:
        return redirect('desembaralha_lobby', codigo=codigo)

    if rodada.fase == partida.fase_atual and not rodada.encerrada:
        _verificar_fim_por_tempo(rodada)

    # A tabela exibida é sempre a da fase "cheia" (não a mini-rodada de
    # desempate usada só para decidir o último colocado em caso de empate).
    rodada_anterior = partida.rodadas.filter(encerrada=True, desempate=False).order_by('-fase').first()
    if rodada_anterior is None:
        return redirect('desembaralha_jogo', codigo=codigo)

    houve_desempate = partida.rodadas.filter(fase=rodada_anterior.fase, desempate=True).exists()
    quadros = sorted(
        rodada_anterior.quadros.select_related('participante__jogador'),
        key=lambda q: -q.acertos,
    )
    return render(request, 'desembaralha/resultado_fase.html', {
        'partida': partida,
        'rodada': rodada_anterior,
        'quadros': quadros,
        'participante': participante,
        'houve_desempate': houve_desempate,
        'proxima_rodada_disponivel': partida.status == Partida.Status.EM_ANDAMENTO and not participante.eliminado,
    })


def campeao(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    if partida.status != Partida.Status.FINALIZADA:
        return redirect('desembaralha_resultado', codigo=codigo)

    campeao_participante = partida.participantes.filter(eliminado=False).first()
    return render(request, 'desembaralha/campeao.html', {
        'partida': partida,
        'campeao': campeao_participante,
    })


def painel_host(request, codigo):
    """Painel do mediador: o host acompanha a partida inteira nesta única
    tela (nunca joga) — QR/lobby até aqui, depois só monitoramento.
    """
    partida = get_object_or_404(Partida, codigo=codigo)
    if not _eh_host(request, partida):
        return redirect('desembaralha_entrar', codigo=codigo)

    return render(request, 'desembaralha/painel_host.html', {'partida': partida})


def estado_host(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    if not _eh_host(request, partida):
        return JsonResponse({'erro': 'Não autorizado.'}, status=403)

    rodada = partida.rodada_atual()
    if rodada is not None:
        _verificar_fim_por_tempo(rodada)
        partida.refresh_from_db()
        rodada = partida.rodada_atual()

    participantes = []
    for p in partida.participantes.select_related('jogador').order_by('-pontos_totais'):
        quadro = QuadroJogador.objects.filter(rodada=rodada, participante=p).first() if rodada else None
        participantes.append({
            'apelido': p.jogador.apelido,
            'pontos_totais': p.pontos_totais,
            'eliminado': p.eliminado,
            'acertos': quadro.acertos if quadro else None,
        })

    campeao_info = None
    if partida.status == Partida.Status.FINALIZADA:
        campeao_participante = partida.participantes.filter(eliminado=False).first()
        if campeao_participante is not None:
            campeao_info = campeao_participante.jogador.apelido

    return JsonResponse({
        'status': partida.status,
        'fase_atual': partida.fase_atual,
        'nivel_atual': partida.nivel_atual,
        'desempate_em_andamento': bool(rodada and rodada.desempate and not rodada.encerrada),
        'tempo_restante': rodada.tempo_restante() if rodada else None,
        'participantes': participantes,
        'campeao': campeao_info,
    })
