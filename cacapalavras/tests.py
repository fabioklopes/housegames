from django.test import TestCase

from . import gerador
from .gerador import CONFIG_NIVEL, gerar_quadro, ordenar_por_desempenho, validar_selecao
from .palavras import BANCO_PALAVRAS


class GeradorQuadroTests(TestCase):
    def test_dimensoes_e_quantidade_de_palavras_por_nivel(self):
        for nivel, config in CONFIG_NIVEL.items():
            grid, palavras = gerar_quadro(nivel)
            self.assertEqual(len(grid), config['tamanho'])
            self.assertTrue(all(len(linha) == config['tamanho'] for linha in grid))
            self.assertLessEqual(len(palavras), config['qtd_palavras'])
            self.assertGreater(len(palavras), 0)

    def test_palavras_posicionadas_realmente_aparecem_no_grid(self):
        for nivel in CONFIG_NIVEL:
            grid, palavras = gerar_quadro(nivel)
            for item in palavras:
                letras = ''.join(grid[r][c] for r, c in item['celulas'])
                self.assertEqual(letras, item['palavra'])
                self.assertFalse(item['encontrada'])

    def test_todas_celulas_preenchidas_sem_nenhuma_vazia(self):
        grid, _ = gerar_quadro('facil')
        for linha in grid:
            for letra in linha:
                self.assertIsNotNone(letra)
                self.assertTrue(letra.isalpha())

    def test_cor_fixa_por_palavra_e_dentro_da_paleta(self):
        grid, palavras = gerar_quadro('medio')
        for item in palavras:
            self.assertIn(item['cor'], gerador.CANDY_PALETTE)

    def test_palavras_nao_ultrapassam_tamanho_do_grid(self):
        for nivel, config in CONFIG_NIVEL.items():
            for ascii_form, _ in BANCO_PALAVRAS[nivel]:
                self.assertLessEqual(len(ascii_form), config['tamanho'])


class ValidarSelecaoTests(TestCase):
    def _grid_simples(self):
        # CASA na primeira linha, na horizontal.
        return [
            list('CASAXXXX'),
            list('XXXXXXXX'),
            list('XXXXXXXX'),
        ]

    def _lista_palavras(self):
        return [
            {'palavra': 'CASA', 'exibida': 'Casa', 'celulas': [[0, 0], [0, 1], [0, 2], [0, 3]],
             'cor': '#FF6F91', 'encontrada': False},
        ]

    def test_palavra_da_lista_marca_encontrada(self):
        grid = self._grid_simples()
        lista = self._lista_palavras()
        resultado = validar_selecao([(0, 0), (0, 1), (0, 2), (0, 3)], grid, lista, [])
        self.assertEqual(resultado['tipo'], 'lista')
        self.assertEqual(resultado['palavra'], 'Casa')
        self.assertTrue(lista[0]['encontrada'])

    def test_palavra_da_lista_aceita_selecao_invertida(self):
        grid = self._grid_simples()
        lista = self._lista_palavras()
        resultado = validar_selecao([(0, 3), (0, 2), (0, 1), (0, 0)], grid, lista, [])
        self.assertEqual(resultado['tipo'], 'lista')
        self.assertTrue(lista[0]['encontrada'])

    def test_palavra_valida_fora_da_lista_e_bonus(self):
        grid = [
            list('MESAXXXX'),
            list('XXXXXXXX'),
            list('XXXXXXXX'),
        ]
        lista = []
        resultado = validar_selecao([(0, 0), (0, 1), (0, 2), (0, 3)], grid, lista, [])
        self.assertEqual(resultado['tipo'], 'bonus')
        self.assertEqual(resultado['palavra'], 'Mesa')

    def test_bonus_nao_pode_ser_reivindicado_duas_vezes(self):
        grid = [list('MESAXXXX'), list('XXXXXXXX'), list('XXXXXXXX')]
        bonus_encontrados = []
        primeiro = validar_selecao([(0, 0), (0, 1), (0, 2), (0, 3)], grid, [], bonus_encontrados)
        segundo = validar_selecao([(0, 0), (0, 1), (0, 2), (0, 3)], grid, [], bonus_encontrados)
        self.assertEqual(primeiro['tipo'], 'bonus')
        self.assertEqual(segundo['tipo'], 'invalida')

    def test_selecao_sem_palavra_valida_e_invalida(self):
        grid = self._grid_simples()
        resultado = validar_selecao([(0, 4), (0, 5), (0, 6)], grid, [], [])
        self.assertEqual(resultado['tipo'], 'invalida')

    def test_selecao_em_linha_reta_nao_reconhecida_marca_para_avaliacao(self):
        # "XXX" é uma linha reta válida, mas não está na lista nem no banco:
        # deve vir marcada para o caller registrar como pendência.
        grid = self._grid_simples()
        resultado = validar_selecao([(0, 4), (0, 5), (0, 6)], grid, [], [])
        self.assertEqual(resultado['tipo'], 'invalida')
        self.assertTrue(resultado.get('linha_reta'))
        self.assertEqual(resultado.get('palavra_formada'), 'XXX')

    def test_selecao_fora_de_linha_reta_e_invalida(self):
        grid = self._grid_simples()
        resultado = validar_selecao([(0, 0), (1, 1), (2, 0)], grid, [], [])
        self.assertEqual(resultado['tipo'], 'invalida')
        self.assertNotIn('linha_reta', resultado)


class OrdenarPorDesempenhoTests(TestCase):
    def test_quem_encontra_mais_palavras_fica_em_primeiro_menos_por_ultimo(self):
        info = [
            {'participante_id': 1, 'encontradas': 2, 'completou': False, 'terminou_em': None},
            {'participante_id': 2, 'encontradas': 6, 'completou': True, 'terminou_em': None},
            {'participante_id': 3, 'encontradas': 0, 'completou': False, 'terminou_em': None},
        ]
        ordenado = ordenar_por_desempenho(info, seed='ABC123-1')
        self.assertEqual(ordenado[0]['participante_id'], 2)
        self.assertEqual(ordenado[-1]['participante_id'], 3)

    def test_quem_termina_mais_rapido_vence_empate_de_palavras_encontradas(self):
        from django.utils import timezone

        agora = timezone.now()
        depois = agora + timezone.timedelta(seconds=5)
        info = [
            {'participante_id': 1, 'encontradas': 6, 'completou': True, 'terminou_em': depois},
            {'participante_id': 2, 'encontradas': 6, 'completou': True, 'terminou_em': agora},
        ]
        ordenado = ordenar_por_desempenho(info, seed='ABC123-1')
        self.assertEqual(ordenado[0]['participante_id'], 2)
        self.assertEqual(ordenado[-1]['participante_id'], 1)

    def test_empate_total_e_resolvido_de_forma_deterministica_pela_seed(self):
        info = [
            {'participante_id': 1, 'encontradas': 0, 'completou': False, 'terminou_em': None},
            {'participante_id': 2, 'encontradas': 0, 'completou': False, 'terminou_em': None},
        ]
        primeira = ordenar_por_desempenho(info, seed='partida-1')
        segunda = ordenar_por_desempenho(info, seed='partida-1')
        self.assertEqual(
            [item['participante_id'] for item in primeira],
            [item['participante_id'] for item in segunda],
        )
