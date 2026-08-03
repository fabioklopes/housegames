from django.urls import path

from . import views

urlpatterns = [
    path('', views.criar_partida, name='cacapalavras_criar'),
    path('lobby/<str:codigo>/', views.lobby, name='cacapalavras_lobby'),
    path('lobby/<str:codigo>/status/', views.lobby_status, name='cacapalavras_lobby_status'),
    path('lobby/<str:codigo>/qrcode/', views.qrcode_imagem, name='cacapalavras_qrcode'),
    path('lobby/<str:codigo>/iniciar/', views.iniciar_partida, name='cacapalavras_iniciar'),
    path('entrar/<str:codigo>/', views.entrar, name='cacapalavras_entrar'),
    path('jogo/<str:codigo>/', views.jogo, name='cacapalavras_jogo'),
    path('jogo/<str:codigo>/estado/', views.estado_jogo, name='cacapalavras_estado'),
    path('jogo/<str:codigo>/validar/', views.validar_palavra, name='cacapalavras_validar'),
    path('resultado/<str:codigo>/', views.resultado_fase, name='cacapalavras_resultado'),
    path('campeao/<str:codigo>/', views.campeao, name='cacapalavras_campeao'),
    path('painel/<str:codigo>/', views.painel_host, name='cacapalavras_painel_host'),
    path('painel/<str:codigo>/estado/', views.estado_host, name='cacapalavras_estado_host'),
]
