# main.py
import warnings
warnings.filterwarnings(
    "ignore",
    message=r"Your system is avx2 capable.*",
    category=RuntimeWarning,
    module="importlib"
)

import pygame
import sys
import quarto   # chama o loop principal que está em quarto.py
import game     # chama o loop principal que está em game.py

pygame.init()
pygame.mixer.init()

# ------------------ MÚSICA ------------------ #
try:
    pygame.mixer.music.load("soundtrack.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"⚠️  Trilha sonora não carregada: {e}")

# ------------------ CONSTANTES ------------------ #
WIDTH, HEIGHT = 1200, 800
BRANCO        = (255, 255, 255)
PRETO         = (  0,   0,   0)
MARROM        = (139,  69,  19)
BTN_NORMAL    = (240, 240, 240)
BTN_HOVER     = (200, 200, 200)
PIXEL_FONT    = "/home/pedro/es2025/fonts/PressStart2P-Regular.ttf"

# ------------------ JANELA ------------------ #
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ICEx Odissey")
clock = pygame.time.Clock()

# ------------------ RECURSOS GRÁFICOS ------------------ #
background = pygame.image.load("home_bg.png").convert()

_font_warn_once = False
def load_font(path, size):
    global _font_warn_once
    try:
        return pygame.font.Font(path, size)
    except FileNotFoundError:
        if not _font_warn_once:
            print(f"⚠️  Fonte '{path}' não encontrada – usando padrão do sistema.")
            _font_warn_once = True
        return pygame.font.Font(None, size)

font_title  = load_font(PIXEL_FONT, 96)
font_button = load_font(PIXEL_FONT, 48)
font_small  = load_font(PIXEL_FONT, 36)

# ------------------ RENDER SHADOW (2 CAMADAS) ------------------ #
def render_shadow(text, font, fg, shadow_color=PRETO, offset=(3,3)):
    base   = font.render(text, True, fg)
    shadow = font.render(text, True, shadow_color)
    surf = pygame.Surface((base.get_width()+offset[0], base.get_height()+offset[1]),
                          pygame.SRCALPHA)
    surf.blit(shadow, offset)
    surf.blit(base, (0,0))
    return surf

# ------------------ BOTÕES ------------------ #
def make_button(texto, center):
    txt = render_shadow(texto, font_button, PRETO, offset=(1,1))
    txt_rect = txt.get_rect(center=center)
    btn_rect = txt_rect.inflate(50, 30)
    return txt, txt_rect, btn_rect

def make_back_button():
    txt = render_shadow("← Voltar", font_small, PRETO, offset=(1,1))
    txt_rect = txt.get_rect(topleft=(20, 20))
    btn_rect = txt_rect.inflate(30, 20)
    esc_txt  = font_small.render("Esc", True, BRANCO)
    esc_rect = esc_txt.get_rect(midtop=(btn_rect.centerx, btn_rect.bottom + 8))
    return txt, txt_rect, btn_rect, esc_txt, esc_rect

# -------------- TELAS -------------- #
def tela_config():
    bar_rect = pygame.Rect(WIDTH/2 - 200, HEIGHT/2, 400, 12)
    knob_r   = 12
    def vol2x(v): return int(bar_rect.left + v*bar_rect.width)
    def x2vol(x): return max(0, min(1, (x - bar_rect.left)/bar_rect.width))

    volume = pygame.mixer.music.get_volume()
    knob_x = vol2x(volume)
    dragging = False

    title = render_shadow("Volume", font_title, BRANCO, offset=(3,3))
    title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/3 - 40))

    back_txt, back_txt_rect, back_rect, esc_txt, esc_rect = make_back_button()

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return
                if ev.key == pygame.K_LEFT:
                    volume = max(0, volume - 0.05)
                if ev.key == pygame.K_RIGHT:
                    volume = min(1, volume + 0.05)
                knob_x = vol2x(volume)
                pygame.mixer.music.set_volume(volume)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if back_rect.collidepoint(ev.pos):
                    return
                if (pygame.Vector2(ev.pos) - pygame.Vector2(knob_x, bar_rect.centery)).length() <= knob_r:
                    dragging = True
                elif bar_rect.collidepoint(ev.pos):
                    knob_x = ev.pos[0]
                    volume = x2vol(ev.pos[0])
                    pygame.mixer.music.set_volume(volume)
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                dragging = False
            if ev.type == pygame.MOUSEMOTION and dragging:
                knob_x = max(bar_rect.left, min(ev.pos[0], bar_rect.right))
                volume = x2vol(knob_x)
                pygame.mixer.music.set_volume(volume)

        # desenho -------------------------
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0,0))
        screen.blit(title, title_rect)

        # barra de volume
        pygame.draw.rect(screen, (80,80,80), bar_rect, border_radius=6)
        filled = bar_rect.copy(); filled.width = knob_x - bar_rect.left
        pygame.draw.rect(screen, (0,255,0), filled, border_radius=6)
        pygame.draw.circle(screen, BRANCO, (knob_x, bar_rect.centery), knob_r)
        pygame.draw.circle(screen, PRETO,  (knob_x, bar_rect.centery), knob_r, 2)

        # volume numérico
        vol_txt = font_small.render(f"{int(volume*100)}%", True, BRANCO)
        screen.blit(vol_txt, vol_txt.get_rect(center=(WIDTH/2, bar_rect.centery + 50)))

        # botão Voltar + indicador Esc
        pygame.draw.rect(screen, BTN_NORMAL, back_rect, border_radius=6)
        pygame.draw.rect(screen, PRETO, back_rect, 2, border_radius=6)
        screen.blit(back_txt, back_txt_rect)
        screen.blit(esc_txt, esc_rect)

        pygame.display.flip()
        clock.tick(60)

def tela_menu():
    txt_start, txt_rect_start, btn_start = make_button("Começar",       (WIDTH/2, HEIGHT/2))
    txt_conf,  txt_rect_conf,  btn_conf  = make_button("Configurações", (WIDTH/2, HEIGHT/2 + 120))

    title_surf = render_shadow("ICEx Odissey", font_title, MARROM, shadow_color=PRETO, offset=(4,4))
    title_rect = title_surf.get_rect(center=(WIDTH/2, HEIGHT/3))

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_start.collidepoint(ev.pos):
                    return
                if btn_conf.collidepoint(ev.pos):
                    tela_config()

        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0,0))
        screen.blit(title_surf, title_rect)

        mouse = pygame.mouse.get_pos()
        for rect, txt_rect, txt_surf in [
            (btn_start, txt_rect_start, txt_start),
            (btn_conf,  txt_rect_conf,  txt_conf)
        ]:
            color = BTN_HOVER if rect.collidepoint(mouse) else BTN_NORMAL
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, PRETO, rect, 2, border_radius=10)
            screen.blit(txt_surf, txt_rect)

        pygame.display.flip()
        clock.tick(60)

# ------------------ EXECUÇÃO ------------------ #
if __name__ == "__main__":
    tela_inicial()   # Mostra a Home Screen
    game.main()    # Inicia o conteúdo do jogo
