from django.urls import path

from . import views

urlpatterns = [
    path('', views.criar_partida, name='desembaralha_criar'),
    path('lobby/<str:codigo>/', views.lobby, name='desembaralha_lobby'),
    path('lobby/<str:codigo>/status/', views.lobby_status, name='desembaralha_lobby_status'),
    path('lobby/<str:codigo>/qrcode/', views.qrcode_imagem, name='desembaralha_qrcode'),
    path('lobby/<str:codigo>/iniciar/', views.iniciar_partida, name='desembaralha_iniciar'),
    path('entrar/<str:codigo>/', views.entrar, name='desembaralha_entrar'),
    path('jogo/<str:codigo>/', views.jogo, name='desembaralha_jogo'),
    path('jogo/<str:codigo>/estado/', views.estado_jogo, name='desembaralha_estado'),
    path('jogo/<str:codigo>/validar/', views.validar_palavra, name='desembaralha_validar'),
    path('resultado/<str:codigo>/', views.resultado_fase, name='desembaralha_resultado'),
    path('campeao/<str:codigo>/', views.campeao, name='desembaralha_campeao'),
    path('painel/<str:codigo>/', views.painel_host, name='desembaralha_painel_host'),
    path('painel/<str:codigo>/estado/', views.estado_host, name='desembaralha_estado_host'),
]
