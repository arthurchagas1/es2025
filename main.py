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

PIXEL_FONT = "PressStart2P-Regular.ttf"   # fonte pixel de 16‑bit (mude se quiser)

# ------------------ JANELA ------------------ #
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ICEx Odissey – Tela Inicial")
clock = pygame.time.Clock()

# ------------------ RECURSOS GRÁFICOS ------------------ #
background = pygame.image.load("home_bg.png").convert()

def carrega_fonte(path: str, tamanho: int) -> pygame.font.Font:
    try:
        return pygame.font.Font(path, tamanho)
    except FileNotFoundError:
        print(f"⚠️  Fonte '{path}' não encontrada – usando padrão do sistema.")
        return pygame.font.Font(None, tamanho)

font_titulo = carrega_fonte(PIXEL_FONT, 96)
font_botao  = carrega_fonte(PIXEL_FONT, 48)

# ------------------ TEXTO 3‑D ------------------ #
def render_3d(texto: str, font: pygame.font.Font, fg: tuple[int,int,int],
              depth: int = 4, offset: tuple[int,int] = (2,2)) -> pygame.Surface:
    """
    Renderiza texto com efeito de extrusão (pseudo 3‑D).
    depth  = número de camadas
    offset = deslocamento de cada camada (x,y)
    """
    base = font.render(texto, True, fg)
    w, h = base.get_size()
    surf = pygame.Surface((w + offset[0]*depth, h + offset[1]*depth), pygame.SRCALPHA)

    # Desenha camadas do fundo para a frente (mais escuras primeiro)
    for i in range(depth, 0, -1):
        shade = tuple(max(0, c - i*25) for c in fg)  # cada camada mais escura
        layer = font.render(texto, True, shade)
        surf.blit(layer, (i*offset[0], i*offset[1]))
    surf.blit(base, (0, 0))  # camada principal
    return surf

# ------------------ FUNÇÕES AUXILIARES ------------------ #
def preparar_botao(texto: str, centro: tuple[int, int]):
    """Cria superfícies e rects para um botão usando fonte pixel."""
    txt_surf = render_3d(texto, font_botao, PRETO, depth=2, offset=(1,1))
    txt_rect = txt_surf.get_rect(center=centro)
    btn_rect = txt_rect.inflate(50, 30)   # área clicável maior
    return txt_surf, txt_rect, btn_rect

# ------------------ TELA INICIAL ------------------ #
def tela_inicial():
    # Botões (Preparados uma única vez)
    txt_start, txt_rect_start, btn_start = preparar_botao("Começar",      (WIDTH/2, HEIGHT/2))
    txt_conf,  txt_rect_conf,  btn_conf  = preparar_botao("Configurações", (WIDTH/2, HEIGHT/2 + 120))

    # Título 3‑D
    titulo_surf = render_3d("ICEx Odissey", font_titulo, BRANCO, depth=6, offset=(3,3))
    titulo_rect = titulo_surf.get_rect(center=(WIDTH/2, HEIGHT/3))

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                return
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_start.collidepoint(evento.pos):
                    return
                if btn_conf.collidepoint(evento.pos):
                    print("⚙️  Tela de configurações ainda não implementada.")

        # -------- Renderização -------- #
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))

        screen.blit(titulo_surf, titulo_rect)

        mouse_pos = pygame.mouse.get_pos()
        for rect, txt_rect, txt_surf in [
            (btn_start, txt_rect_start, txt_start),
            (btn_conf,  txt_rect_conf,  txt_conf)
        ]:
            cor = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_NORMAL
            pygame.draw.rect(screen, cor, rect, border_radius=10)
            pygame.draw.rect(screen, PRETO, rect, 2, border_radius=10)
            screen.blit(txt_surf, txt_rect)

        pygame.display.flip()
        clock.tick(60)

# ------------------ EXECUÇÃO ------------------ #
if __name__ == "__main__":
    tela_inicial()
    quarto.main()
