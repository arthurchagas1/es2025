import pygame
import sys
import os
import game  # importa o jogo principal (game.py)

pygame.init()

# -------------- PROPORÇÃO 16:9 --------------
LARGURA = 1280
ALTURA  = 720
tela    = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Ônibus")

# Cores
BRANCO = (255, 255, 255)
PRETO  = (  0,   0,   0)

clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 24)

# —————— Fonte pixel e madeira ——————
PIXEL_FONT = "PressStart2P.ttf"
try:
    pixel_font = pygame.font.Font(PIXEL_FONT, 16)
except FileNotFoundError:
    pixel_font = fonte

wood_tex = pygame.image.load("wood.png").convert()

def render_text_with_border(text: str, fg, border, font, border_size=2):
    base = font.render(text, True, fg)
    w, h = base.get_width() + border_size*2, base.get_height() + border_size*2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in (-border_size, 0, border_size):
        for dy in (-border_size, 0, border_size):
            if dx or dy:
                surf.blit(font.render(text, True, border), (dx+border_size, dy+border_size))
    surf.blit(base, (border_size, border_size))
    return surf

def show_welcome_onibus(fundo):
    popup_w, popup_h = 800, 300
    # Painel de madeira
    popup = pygame.transform.scale(wood_tex, (popup_w, popup_h))
    pygame.draw.rect(popup, PRETO, popup.get_rect(), 4)

    # Texto quebrado em linhas
    linhas = [
        "Bem vindo ao jogo,",
        "ao sair do onibus voce entrara",
        "nos dominios da ufmg onde voce",
        "tera diversas missoes"
    ]
    # Renderiza cada linha com borda
    for i, l in enumerate(linhas):
        txt = render_text_with_border(l, BRANCO, PRETO, pixel_font, border_size=2)
        popup.blit(txt, (20, 20 + i * (pixel_font.get_height() + 8)))

    rect = popup.get_rect(center=(LARGURA//2, ALTURA//2))
    esperando = True
    while esperando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                esperando = False

        # Desenha fundo do ônibus escurecido
        tela.blit(fundo, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))

        # Desenha popup
        tela.blit(popup, rect.topleft)
        pygame.display.flip()
        clock.tick(60)


# -------------- CARREGANDO AS IMAGENS ANIMADAS --------------
def load_animation_frames(folder="animacoes", scale_factor=0.45):
    frames = []
    for i in range(16):
        path = os.path.join(folder, f"frame_{i}.png")
        img = pygame.image.load(path).convert_alpha()
        ow, oh = img.get_size()
        frames.append(pygame.transform.scale(img, (int(ow*scale_factor), int(oh*scale_factor))))
    return {
        "down":  frames[0:4],
        "left":  frames[8:12],
        "right": frames[12:16],
        "up":    frames[4:8],
    }

class Jogador(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()
        self.animations        = animations
        self.current_direction = "down"
        self.frame_index       = 0
        self.frame_speed       = 0.15
        self.image             = animations["down"][0]
        self.rect              = self.image.get_rect(center=(LARGURA//2, ALTURA//2))
        self.velocidade        = 5

    def update(self, teclas):
        old = self.rect.copy()
        mov = False
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidade; self.current_direction = "left";  mov = True
        elif teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidade; self.current_direction = "right"; mov = True
        elif teclas[pygame.K_UP]:
            self.rect.y -= self.velocidade; self.current_direction = "up";    mov = True
        elif teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidade; self.current_direction = "down";  mov = True

        # mantém dentro das bordas superior, inferior e direita
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        # animação
        if mov:
            seq = self.animations[self.current_direction]
            self.frame_index = (self.frame_index + self.frame_speed) % len(seq)
        else:
            self.frame_index = 0
        self.image = self.animations[self.current_direction][int(self.frame_index)]

def main():
   # carrega fundo
    fundo = pygame.transform.scale(
        pygame.image.load("onibus.png").convert(),
        (LARGURA, ALTURA)
    )

    # exibe popup de boas-vindas
    show_welcome_onibus(fundo)

    # continua com o resto do main...
    animations = load_animation_frames("animacoes", scale_factor=0.45)
    jogador    = Jogador(animations)
    grupo      = pygame.sprite.Group(jogador)
    asking_exit = False

    rodando = True
    while rodando:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False

            # se estiver no prompt de saída, espera S ou N
            if asking_exit and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s:      # 'S' para Sim
                    game.main()
                    return
                elif e.key == pygame.K_n:    # 'N' para Não
                    asking_exit = False

        if not asking_exit:
            teclas = pygame.key.get_pressed()
            jogador.update(teclas)
            # se tentar sair para a esquerda
            if jogador.rect.left <= 0:
                # trava na borda e abre prompt
                jogador.rect.left = 0
                asking_exit = True

        # desenha cenário e jogador
        tela.blit(fundo, (0, 0))
        grupo.draw(tela)

        # se no prompt, desenha a janelinha
        if asking_exit:
            w, h = 700, 200
            # fundo de madeira
            popup = pygame.transform.scale(wood_tex, (w, h))
            rect  = popup.get_rect(center=(LARGURA//2, ALTURA//2))
            # borda preta
            pygame.draw.rect(popup, PRETO, popup.get_rect(), 2)

            # textos em branco com borda preta
            txt1 = render_text_with_border("Deseja ir para a UFMG?", BRANCO, PRETO, pixel_font, border_size=2)
            txt2 = render_text_with_border("S: Sim    N: Não",        BRANCO, PRETO, pixel_font, border_size=2)

            popup.blit(txt1, ((w - txt1.get_width()) // 2,  50))
            popup.blit(txt2, ((w - txt2.get_width()) // 2, 120))
            tela.blit(popup, rect.topleft)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
