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
    popup = pygame.transform.scale(wood_tex, (popup_w, popup_h))
    pygame.draw.rect(popup, PRETO, popup.get_rect(), 4)

    linhas = [
        "Bem vindo ao jogo,",
        "ao sair do onibus voce entrara",
        "nos dominios da ufmg onde voce",
        "tera diversas missoes"
    ]
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

        tela.blit(fundo, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))
        tela.blit(popup, rect.topleft)
        pygame.display.flip()
        clock.tick(60)

# -------------- CARREGANDO O MASK DE COLISÃO --------------
raw_mask = pygame.image.load("onibus_mask.png").convert()
# redimensiona para exatamente o mesmo tamanho do fundo (LARGURA×ALTURA)
mask_surf = pygame.transform.scale(raw_mask, (LARGURA, ALTURA))
# gera a máscara considerando tons próximos ao vermelho
collision_mask = pygame.mask.from_threshold(mask_surf, (255,0,0), (50,50,50))

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
        # exemplo: 75% da altura da tela
        self.rect = self.image.get_rect(center=(LARGURA//2.3, int(ALTURA * 0.85)))

        self.velocidade        = 5
        self.mask              = pygame.mask.from_surface(self.image)

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

        # Mantém dentro das bordas superior, inferior e direita
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        # Animação
        if mov:
            seq = self.animations[self.current_direction]
            self.frame_index = (self.frame_index + self.frame_speed) % len(seq)
        else:
            self.frame_index = 0
        self.image = self.animations[self.current_direction][int(self.frame_index)]
        # Atualiza máscara do jogador
        self.mask = pygame.mask.from_surface(self.image)

        # Colisão pixel-a-pixel: se sobrepor ao collision_mask, reverte
        if collision_mask.overlap(self.mask, (self.rect.x, self.rect.y)):
            self.rect = old

def main():
    # Carrega fundo e exibe boas-vindas
    fundo = pygame.transform.scale(pygame.image.load("onibus.png").convert(), (LARGURA, ALTURA))
    show_welcome_onibus(fundo)

    animations  = load_animation_frames("animacoes", scale_factor=0.21)
    jogador     = Jogador(animations)
    grupo       = pygame.sprite.Group(jogador)
    asking_exit = False

    rodando = True
    while rodando:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if asking_exit and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s:
                    game.main()
                    return
                elif e.key == pygame.K_n:
                    asking_exit = False

        teclas = pygame.key.get_pressed()
        if not asking_exit:
            jogador.update(teclas)
            # se tentar sair para a esquerda
            if jogador.rect.left <= 0:
                jogador.rect.left = 0
                asking_exit = True

        # Desenha cenário e jogador
        tela.blit(fundo, (0, 0))

        mask_surf = collision_mask.to_surface(setcolor=(255,0,0), unsetcolor=(0,0,0,0))
        mask_surf.set_alpha(0)
        tela.blit(mask_surf, (0, 0))
        grupo.draw(tela)

        # Prompt de saída
        if asking_exit:
            w, h = 700, 200
            popup = pygame.transform.scale(wood_tex, (w, h))
            pygame.draw.rect(popup, PRETO, popup.get_rect(), 2)
            txt1 = render_text_with_border("Deseja ir para a UFMG?", BRANCO, PRETO, pixel_font, border_size=2)
            txt2 = render_text_with_border("S: Sim    N: Não",        BRANCO, PRETO, pixel_font, border_size=2)
            popup.blit(txt1, ((w - txt1.get_width()) // 2,  50))
            popup.blit(txt2, ((w - txt2.get_width()) // 2, 120))
            rect = popup.get_rect(center=(LARGURA//2, ALTURA//2))
            tela.blit(popup, rect.topleft)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
