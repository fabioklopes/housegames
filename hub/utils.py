from .models import Jogador


def obter_jogador_sessao(request):
    if not request.session.session_key:
        return None
    return Jogador.objects.filter(session_key=request.session.session_key).first()


def criar_ou_atualizar_jogador(request, apelido):
    if not request.session.session_key:
        request.session.save()
    jogador, _ = Jogador.objects.update_or_create(
        session_key=request.session.session_key,
        defaults={'apelido': apelido[:30]},
    )
    return jogador
