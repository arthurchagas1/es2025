# main.py
import pygame
import sys
import quarto   # chama o loop principal que está em quarto.py

pygame.init()

# ------------------ CONSTANTES ------------------ #
WIDTH, HEIGHT = 1200, 800
BRANCO        = (255, 255, 255)
PRETO         = (  0,   0,   0)
BTN_NORMAL    = (240, 240, 240)
BTN_HOVER     = (200, 200, 200)

# ------------------ JANELA ------------------ #
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ICEx Odissey – Tela Inicial")
clock = pygame.time.Clock()

# ------------------ RECURSOS GRÁFICOS ------------------ #
# Coloque uma imagem chamada 'home_bg.png' na mesma pasta, ou troque o caminho aqui:
background = pygame.image.load("home_bg.png").convert()

font_titulo = pygame.font.Font(None, 96)
font_botao  = pygame.font.Font(None, 60)

# ------------------ FUNÇÕES AUXILIARES ------------------ #
def preparar_botao(texto: str, centro: tuple[int, int]):
    """Cria texto renderizado e rects para um botão."""
    txt_surf = font_botao.render(texto, True, PRETO)
    txt_rect = txt_surf.get_rect(center=centro)
    btn_rect = txt_rect.inflate(40, 20)          # área clicável maior que o texto
    return txt_surf, txt_rect, btn_rect

# ------------------ TELA INICIAL ------------------ #
def tela_inicial():
    # Botões (depositamos todas as superfícies e rects em variáveis)
    txt_start, txt_rect_start, btn_start = preparar_botao("Começar",      (WIDTH / 2, HEIGHT / 2))
    txt_conf,  txt_rect_conf,  btn_conf  = preparar_botao("Configurações", (WIDTH / 2, HEIGHT / 2 + 100))

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                return  # Começa o jogo pelo Enter
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_start.collidepoint(evento.pos):
                    return  # Começa o jogo clicando em Começar
                if btn_conf.collidepoint(evento.pos):
                    print("⚙️  Tela de configurações ainda não implementada.")

        # -------- Renderização -------- #
        # Fundo
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))

        # Título com leve sombra
        sombra = font_titulo.render("ICEx Odissey", True, PRETO)
        sombra_rect = sombra.get_rect(center=(WIDTH / 2 + 3, HEIGHT / 3 + 3))
        screen.blit(sombra, sombra_rect)
        titulo = font_titulo.render("ICEx Odissey", True, BRANCO)
        titulo_rect = titulo.get_rect(center=(WIDTH / 2, HEIGHT / 3))
        screen.blit(titulo, titulo_rect)

        # Botões
        mouse_pos = pygame.mouse.get_pos()
        for rect, txt_rect, txt_surf in [
            (btn_start, txt_rect_start, txt_start),
            (btn_conf,  txt_rect_conf,  txt_conf)
        ]:
            cor = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_NORMAL
            pygame.draw.rect(screen, cor, rect, border_radius=8)
            pygame.draw.rect(screen, PRETO, rect, 2, border_radius=8)
            screen.blit(txt_surf, txt_rect)

        pygame.display.flip()
        clock.tick(60)

# ------------------ EXECUÇÃO ------------------ #
if __name__ == "__main__":
    tela_inicial()   # Mostra a Home Screen
    quarto.main()    # Inicia o conteúdo do jogo
