import warnings
import quarto
warnings.filterwarnings(
    "ignore",
    message=r"Your system is avx2 capable.*",
    category=RuntimeWarning,
    module="importlib"
)

import pygame, sys, game

pygame.init()
pygame.mixer.init()

# ─── MÚSICA ──────────────────────────────────────────
try:
    pygame.mixer.music.load("soundtrack.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"⚠️  Trilha sonora não carregada: {e}")

# ─── CONSTANTES ─────────────────────────────────────
WIDTH, HEIGHT = 1200, 800
BRANCO, PRETO  = (255,255,255), (0,0,0)
MARROM         = (139,69,19)
BTN_NORMAL     = (240,240,240)
BTN_HOVER      = (200,200,200)
PIXEL_FONT     = "PressStart2P.ttf"  # ajuste se necessário

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ICEx Odissey")
clock = pygame.time.Clock()

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

# ─── TEXTO COM SOMBRA (2 LAYERS) ────────────────────
def render_shadow(text, font, fg, shadow_color=PRETO, offset=(3,3)):
    base   = font.render(text, True, fg)
    shadow = font.render(text, True, shadow_color)
    surf = pygame.Surface((base.get_width()+offset[0], base.get_height()+offset[1]), pygame.SRCALPHA)
    surf.blit(shadow, offset); surf.blit(base, (0,0))
    return surf

# ─── BOTÕES ─────────────────────────────────────────
def make_button(text, center):
    surf = render_shadow(text, font_button, PRETO, offset=(1,1))
    txt_rect = surf.get_rect(center=center)
    btn_rect = txt_rect.inflate(50,30)
    return surf, txt_rect, btn_rect

def make_back_button():
    surf = render_shadow("← Voltar", font_small, PRETO, offset=(1,1))
    txt_rect = surf.get_rect(topleft=(20,20))
    btn_rect = txt_rect.inflate(30,20)
    esc_surf = font_small.render("Esc", True, BRANCO)
    esc_rect = esc_surf.get_rect(midtop=(btn_rect.centerx, btn_rect.bottom+8))
    return surf, txt_rect, btn_rect, esc_surf, esc_rect

# ─── TELA DE CONFIGURAÇÕES / PAUSA ──────────────────
def tela_config(bg_surface=None):
    """
    Se bg_surface != None → modo pausa (frame congelado ao fundo)
    Retorna "menu" se o jogador escolher voltar ao menu inicial,
    ou None caso contrário.
    """
    bar = pygame.Rect(WIDTH//2-200, HEIGHT//2, 400, 12)
    knob_r   = 12
    volume   = pygame.mixer.music.get_volume()
    knob_x   = bar.left + int(volume*bar.width)
    dragging = False

    title   = render_shadow("Volume", font_title, BRANCO, offset=(3,3))
    title_r = title.get_rect(center=(WIDTH/2, HEIGHT/3 - 40))

    back_surf, back_txt_r, back_btn, esc_surf, esc_rect = make_back_button()
    # botão "Menu Inicial" só no modo pausa
    if bg_surface is not None:
        menu_surf, menu_txt_r, menu_btn = make_button("Menu Inicial", (WIDTH/2, HEIGHT/2 + 180))

    def draw_bg():
        if bg_surface is None:
            screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0,0))
        else:
            screen.blit(bg_surface, (0,0))
            dim = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA); dim.fill((0,0,0,180))
            screen.blit(dim,(0,0))

    def x_to_vol(x): return max(0,min(1,(x - bar.left)/bar.width))

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return
                if ev.key == pygame.K_LEFT:  volume=max(0,volume-0.05)
                if ev.key == pygame.K_RIGHT: volume=min(1,volume+0.05)
                if ev.key == pygame.K_m and bg_surface is not None:
                    return "menu"
                knob_x = bar.left + int(volume*bar.width)
                pygame.mixer.music.set_volume(volume)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if back_btn.collidepoint(ev.pos): return
                if bg_surface is not None and menu_btn.collidepoint(ev.pos): return "menu"
                if (pygame.Vector2(ev.pos)-pygame.Vector2(knob_x, bar.centery)).length()<=knob_r:
                    dragging = True
                elif bar.collidepoint(ev.pos):
                    knob_x = ev.pos[0]; volume = x_to_vol(knob_x); pygame.mixer.music.set_volume(volume)
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                dragging = False
            if ev.type == pygame.MOUSEMOTION and dragging:
                knob_x = max(bar.left, min(ev.pos[0], bar.right))
                volume = x_to_vol(knob_x); pygame.mixer.music.set_volume(volume)

        # --- desenho ---
        draw_bg()
        screen.blit(title, title_r)

        pygame.draw.rect(screen, (80,80,80), bar, border_radius=6)
        filled = bar.copy(); filled.width = knob_x - bar.left
        pygame.draw.rect(screen, (0,255,0), filled, border_radius=6)
        pygame.draw.circle(screen, BRANCO, (knob_x, bar.centery), knob_r)
        pygame.draw.circle(screen, PRETO,  (knob_x, bar.centery), knob_r, 2)

        v_txt = font_small.render(f"{int(volume*100)}%", True, BRANCO)
        screen.blit(v_txt, v_txt.get_rect(center=(WIDTH/2, bar.centery+50)))

        pygame.draw.rect(screen, BTN_NORMAL, back_btn, border_radius=6)
        pygame.draw.rect(screen, PRETO, back_btn, 2, border_radius=6)
        screen.blit(back_surf, back_txt_r); screen.blit(esc_surf, esc_rect)

        if bg_surface is not None:
            mouse = pygame.mouse.get_pos()
            col = BTN_HOVER if menu_btn.collidepoint(mouse) else BTN_NORMAL
            pygame.draw.rect(screen, col, menu_btn, border_radius=10)
            pygame.draw.rect(screen, PRETO, menu_btn, 2, border_radius=10)
            screen.blit(menu_surf, menu_txt_r)

        pygame.display.flip(); clock.tick(60)

# ─── MENU INICIAL ───────────────────────────────────
def tela_menu():
    start_s, start_r, btn_start = make_button("Começar", (WIDTH/2, HEIGHT/2))
    conf_s , conf_r , btn_conf  = make_button("Configurações", (WIDTH/2, HEIGHT/2 + 120))

    title = render_shadow("ICEx Odissey", font_title, MARROM, shadow_color=PRETO, offset=(4,4))
    title_r = title.get_rect(center=(WIDTH/2, HEIGHT/3))

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN: return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_start.collidepoint(ev.pos): return
                if btn_conf .collidepoint(ev.pos): tela_config()

        screen.blit(pygame.transform.scale(background,(WIDTH,HEIGHT)),(0,0))
        screen.blit(title,title_r)

        mouse = pygame.mouse.get_pos()
        for rect,txt_r,txt_s in [(btn_start,start_r,start_s),(btn_conf,conf_r,conf_s)]:
            cor = BTN_HOVER if rect.collidepoint(mouse) else BTN_NORMAL
            pygame.draw.rect(screen, cor, rect, border_radius=10)
            pygame.draw.rect(screen, PRETO, rect, 2, border_radius=10)
            screen.blit(txt_s, txt_r)

        pygame.display.flip(); clock.tick(60)

# ─── LOOP PRINCIPAL ─────────────────────────────────
if __name__ == "__main__":
    tela_menu()
    game.main()
