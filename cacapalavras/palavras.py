"""Banco de palavras curado em pt-BR (nova ortografia) para o Caça-Palavras.

Cada entrada é uma tupla (FORMA_ASCII, "Forma exibida acentuada").
A forma ASCII (maiúscula, sem acento) é a que aparece no tabuleiro;
a forma acentuada é exibida na lista de palavras do jogador.
"""

BANCO_PALAVRAS = {
    'facil': [
        ('CASA', 'Casa'), ('MESA', 'Mesa'), ('BOLA', 'Bola'), ('GATO', 'Gato'),
        ('RATO', 'Rato'), ('PATO', 'Pato'), ('LIVRO', 'Livro'), ('FESTA', 'Festa'),
        ('PRAIA', 'Praia'), ('NUVEM', 'Nuvem'), ('FOGAO', 'Fogão'), ('LUGAR', 'Lugar'),
        ('MOEDA', 'Moeda'), ('PORTA', 'Porta'), ('JANELA', 'Janela'), ('CAMISA', 'Camisa'),
        ('SAPATO', 'Sapato'), ('CHUVA', 'Chuva'), ('FLOR', 'Flor'), ('ARVORE', 'Árvore'),
        ('BANANA', 'Banana'), ('MACA', 'Maçã'), ('PERA', 'Pera'), ('MELAO', 'Melão'),
        ('LIMAO', 'Limão'), ('COCO', 'Coco'), ('FEIJAO', 'Feijão'), ('ARROZ', 'Arroz'),
        ('LEITE', 'Leite'), ('QUEIJO', 'Queijo'), ('PEIXE', 'Peixe'), ('CARNE', 'Carne'),
        ('FRANGO', 'Frango'), ('ESCOLA', 'Escola'), ('AMIGO', 'Amigo'), ('CIDADE', 'Cidade'),
        ('PARQUE', 'Parque'), ('FLORES', 'Flores'), ('JARDIM', 'Jardim'), ('CARRO', 'Carro'),
        ('TREM', 'Trem'), ('AVIAO', 'Avião'), ('BARCO', 'Barco'), ('ONIBUS', 'Ônibus'),
        ('PONTE', 'Ponte'), ('MONTE', 'Monte'), ('VENTO', 'Vento'), ('NEVE', 'Neve'),
        ('FRIO', 'Frio'), ('CALOR', 'Calor'), ('VERAO', 'Verão'),
    ],
    'medio': [
        ('LARANJA', 'Laranja'), ('ABACAXI', 'Abacaxi'), ('MORANGO', 'Morango'),
        ('FAMILIA', 'Família'), ('ESTRADA', 'Estrada'), ('INVERNO', 'Inverno'),
        ('CACHORRO', 'Cachorro'), ('ELEFANTE', 'Elefante'), ('GIRAFA', 'Girafa'),
        ('MACACO', 'Macaco'), ('TESOURO', 'Tesouro'), ('CASTELO', 'Castelo'),
        ('PRINCESA', 'Princesa'), ('DRAGAO', 'Dragão'), ('FLORESTA', 'Floresta'),
        ('MONTANHA', 'Montanha'), ('FUTEBOL', 'Futebol'), ('BASQUETE', 'Basquete'),
        ('NATACAO', 'Natação'), ('CORRIDA', 'Corrida'), ('PATINETE', 'Patinete'),
        ('AVENTURA', 'Aventura'), ('VIAGEM', 'Viagem'), ('FERIADO', 'Feriado'),
        ('FERIAS', 'Férias'), ('AMIZADE', 'Amizade'), ('FAMOSO', 'Famoso'),
        ('ALEGRIA', 'Alegria'), ('TRISTEZA', 'Tristeza'), ('CORAGEM', 'Coragem'),
        ('VITORIA', 'Vitória'), ('DERROTA', 'Derrota'), ('SAUDADE', 'Saudade'),
        ('CARINHO', 'Carinho'), ('RESPEITO', 'Respeito'), ('JUSTICA', 'Justiça'),
        ('GENEROSO', 'Generoso'), ('CRIANCA', 'Criança'), ('ADULTO', 'Adulto'),
        ('CADERNO', 'Caderno'), ('BORRACHA', 'Borracha'), ('MOCHILA', 'Mochila'),
        ('UNIFORME', 'Uniforme'), ('RECREIO', 'Recreio'),
    ],
    'dificil': [
        ('TARTARUGA', 'Tartaruga'), ('BORBOLETA', 'Borboleta'), ('CAVALEIRO', 'Cavaleiro'),
        ('CACHOEIRA', 'Cachoeira'), ('RELAMPAGO', 'Relâmpago'), ('TEMPESTADE', 'Tempestade'),
        ('ESPERANCA', 'Esperança'), ('PACIENCIA', 'Paciência'), ('LIBERDADE', 'Liberdade'),
        ('PROFESSOR', 'Professor'), ('ESTUDANTE', 'Estudante'), ('BIBLIOTECA', 'Biblioteca'),
        ('COMPUTADOR', 'Computador'), ('TELEFONE', 'Telefone'), ('TELEVISAO', 'Televisão'),
        ('GELADEIRA', 'Geladeira'), ('LAVANDERIA', 'Lavanderia'), ('VIZINHANCA', 'Vizinhança'),
        ('CRIATIVO', 'Criativo'), ('AMBICIOSO', 'Ambicioso'), ('CORAJOSO', 'Corajoso'),
        ('HABILIDADE', 'Habilidade'), ('VELOCIDADE', 'Velocidade'), ('SEGURANCA', 'Segurança'),
        ('TECNOLOGIA', 'Tecnologia'), ('UNIVERSO', 'Universo'), ('PLANETARIO', 'Planetário'),
        ('ASTRONAUTA', 'Astronauta'), ('FOGUETE', 'Foguete'), ('SATELITE', 'Satélite'),
        ('METEORO', 'Meteoro'), ('GALAXIA', 'Galáxia'), ('ATMOSFERA', 'Atmosfera'),
        ('OCEANO', 'Oceano'), ('TERREMOTO', 'Terremoto'), ('FURACAO', 'Furacão'),
        ('INUNDACAO', 'Inundação'), ('NATUREZA', 'Natureza'), ('AMBIENTE', 'Ambiente'),
        ('POLUICAO', 'Poluição'), ('RECICLAGEM', 'Reciclagem'),
    ],
}


def banco_completo():
    """Dicionário {FORMA_ASCII: forma_exibida} com as palavras de todos os níveis."""
    completo = {}
    for lista in BANCO_PALAVRAS.values():
        for ascii_form, exibida in lista:
            completo[ascii_form] = exibida
    return completo
