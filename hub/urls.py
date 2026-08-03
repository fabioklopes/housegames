from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='hub_index'),
    path('ranking/', views.ranking, name='hub_ranking'),
    path('reiniciar-sessao/', views.reiniciar_sessao, name='hub_reiniciar_sessao'),
    path('nova-secao/', views.nova_secao, name='hub_nova_secao'),
]
