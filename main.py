import pygame
import sys
import quarto   # agora importa o arquivo quarto.py

# Inicialização do pygame
pygame.init()

# Configurações da tela inicial
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tela Inicial")

# Definição de cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

clock = pygame.time.Clock()

# Criação de fontes para os textos
font_titulo = pygame.font.Font(None, 74)
font_start  = pygame.font.Font(None, 50)

def tela_inicial():
    iniciar = False
    while not iniciar:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Usa a tecla Enter ou clique do mouse para iniciar o jogo
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                iniciar = True
            if evento.type == pygame.MOUSEBUTTONDOWN:
                iniciar = True

        # Preenche o fundo com branco
        screen.fill(BRANCO)
        
        # Renderiza o título e o texto do start
        titulo_texto = font_titulo.render("Meu Jogo", True, PRETO)
        start_texto  = font_start.render("Pressione Enter para iniciar", True, PRETO)
        
        # Centraliza os textos
        titulo_rect = titulo_texto.get_rect(center=(WIDTH/2, HEIGHT/3))
        start_rect  = start_texto.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        screen.blit(titulo_texto, titulo_rect)
        screen.blit(start_texto, start_rect)
        
        pygame.display.flip()
        clock.tick(60)

# Executa a tela inicial
tela_inicial()

# Após sair da tela inicial, inicia o conteúdo do quarto.py
quarto.main()
