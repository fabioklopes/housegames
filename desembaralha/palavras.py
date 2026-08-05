"""Banco de palavras curado em pt-BR (nova ortografia) para o Desembaralha.

Cada entrada é a forma exibida (acentuada) da palavra. A comparação com o
que o jogador digita ignora todos os acentos, exceto a cedilha (ver
`gerador.normalizar_palavra`).

Palavras compostas por hífen aparecem apenas onde o hífen faz parte da
grafia oficial da palavra (ex.: "guarda-chuva"); não há palavras compostas
sem hífen nem separadas por espaço.
"""

BANCO_PALAVRAS = {
    'facil': [
        'Casa', 'Mesa', 'Bola', 'Gato', 'Rato', 'Pato', 'Livro', 'Festa',
        'Praia', 'Nuvem', 'Fogão', 'Lugar', 'Moeda', 'Porta', 'Janela',
        'Camisa', 'Sapato', 'Chuva', 'Flor', 'Árvore', 'Banana', 'Maçã',
        'Pera', 'Melão', 'Limão', 'Coco', 'Feijão', 'Arroz', 'Leite',
        'Queijo', 'Peixe', 'Carne', 'Frango', 'Escola', 'Amigo', 'Cidade',
        'Parque', 'Jardim', 'Carro', 'Trem', 'Avião', 'Barco', 'Ônibus',
        'Ponte', 'Monte', 'Vento', 'Neve', 'Frio', 'Calor', 'Verão',
        'Açúcar', 'Cabeça', 'Braço', 'Perna', 'Coração', 'Maçaneta',
    ],
    'medio': [
        'Laranja', 'Abacaxi', 'Morango', 'Família', 'Estrada', 'Inverno',
        'Cachorro', 'Elefante', 'Girafa', 'Macaco', 'Tesouro', 'Castelo',
        'Princesa', 'Dragão', 'Floresta', 'Montanha', 'Futebol', 'Basquete',
        'Natação', 'Corrida', 'Patinete', 'Aventura', 'Viagem', 'Feriado',
        'Férias', 'Amizade', 'Famoso', 'Alegria', 'Tristeza', 'Coragem',
        'Vitória', 'Derrota', 'Saudade', 'Carinho', 'Respeito', 'Justiça',
        'Criança', 'Caderno', 'Borracha', 'Mochila', 'Uniforme', 'Recreio',
        'Almoço', 'Padaria', 'Açougue', 'Serviço', 'Endereço', 'Preguiça',
        'Guarda-chuva', 'Guarda-roupa', 'Guarda-costas', 'Guarda-sol',
        'Beija-flor', 'Vaga-lume', 'Couve-flor', 'Bate-boca',
        'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira',
    ],
    'dificil': [
        'Tartaruga', 'Borboleta', 'Cavaleiro', 'Cachoeira', 'Relâmpago',
        'Tempestade', 'Esperança', 'Paciência', 'Liberdade', 'Professor',
        'Estudante', 'Biblioteca', 'Computador', 'Telefone', 'Televisão',
        'Geladeira', 'Lavanderia', 'Vizinhança', 'Criativo', 'Ambicioso',
        'Corajoso', 'Habilidade', 'Velocidade', 'Segurança', 'Tecnologia',
        'Universo', 'Planetário', 'Astronauta', 'Foguete', 'Satélite',
        'Meteoro', 'Galáxia', 'Atmosfera', 'Oceano', 'Terremoto', 'Furacão',
        'Inundação', 'Natureza', 'Ambiente', 'Poluição', 'Reciclagem',
        'Almoxarifado', 'Cumplicidade', 'Adolescência', 'Circunstância',
        'Arco-íris', 'Bem-te-vi', 'João-de-barro', 'Pé-de-moleque',
        'Decreto-lei', 'Curto-circuito', 'Para-quedas', 'Para-raios',
        'Primeiro-ministro', 'Guarda-noturno', 'Mais-valia', 'Guarda-marinha',
    ],
}
