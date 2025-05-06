import pygame
import sys
import os
import time
from typing import List
import onibus  # ou game, conforme seu fluxo

pygame.init()

# -------------- PROPORÇÃO 16:9 --------------
LARGURA = 1280
ALTURA  = 720
tela    = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Quarto")

# Cores
BRANCO = (255, 255, 255)
PRETO  = (  0,   0,   0)
CINZA  = (100, 100, 100)

clock = pygame.time.Clock()

# —————— FONTE 16-BIT “QUADRADONA” ——————
FONT_SIZE  = 24
PIXEL_FONT = pygame.font.Font("PressStart2P.ttf", FONT_SIZE)

def render_text_with_border(text: str, fg, border, size=2):
    base = PIXEL_FONT.render(text, True, fg)
    w, h = base.get_width()+2*size, base.get_height()+2*size
    surf = pygame.Surface((w,h), pygame.SRCALPHA)
    for dx in (-size,0,size):
        for dy in (-size,0,size):
            if dx or dy:
                surf.blit(PIXEL_FONT.render(text, True, border), (dx+size, dy+size))
    surf.blit(base, (size, size))
    return surf

# -------------- TEXTURAS --------------
wood_tex  = pygame.image.load("wood.png").convert()
bg_quarto = pygame.transform.scale(pygame.image.load("quarto.png").convert(),
                                   (LARGURA, ALTURA))

# -------------- ANIMAÇÕES --------------
def load_animation_frames(folder="animacoes", scale_factor=0.45):
    frames=[]
    for i in range(16):
        img = pygame.image.load(os.path.join(folder, f"frame_{i}.png")).convert_alpha()
        ow, oh = img.get_size()
        frames.append(pygame.transform.scale(img, (int(ow*scale_factor), int(oh*scale_factor))))
    return {
        "down":  frames[0:4],
        "left":  frames[8:12],
        "right": frames[12:16],
        "up":    frames[4:8],
    }

# -------------- CLASSES --------------
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h):
        super().__init__()
        self.image = pygame.Surface((w,h)); self.image.fill(CINZA)
        self.rect  = self.image.get_rect(topleft=(x,y))

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

    def update(self, teclas, obstaculos: List[Obstaculo]):
        old = self.rect.copy(); mv=False
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidade; mv=True; self.current_direction="left"
        elif teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidade; mv=True; self.current_direction="right"
        elif teclas[pygame.K_UP]:
            self.rect.y -= self.velocidade; mv=True; self.current_direction="up"
        elif teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidade; mv=True; self.current_direction="down"

        for o in obstaculos:
            if self.rect.colliderect(o.rect):
                self.rect = old; break
        self.rect.clamp_ip(pygame.Rect(0,0,LARGURA,ALTURA))

        if mv:
            seq = self.animations[self.current_direction]
            self.frame_index = (self.frame_index + self.frame_speed) % len(seq)
        else:
            self.frame_index = 0
        self.image = self.animations[self.current_direction][int(self.frame_index)]

def ajustar_posicao_inicial(jogador: Jogador, obstaculos: List[Obstaculo]):
    while any(jogador.rect.colliderect(o.rect) for o in obstaculos):
        jogador.rect.y -= jogador.velocidade
        if jogador.rect.top <= 0:
            jogador.rect.top = 0
            jogador.rect.x += jogador.velocidade
            if jogador.rect.right >= LARGURA:
                jogador.rect.right = LARGURA
                break

# -------------- INTRO POPUP --------------
def show_intro():
    pw, ph = 800, 300
    wood = pygame.transform.scale(wood_tex, (pw, ph))
    popup = pygame.Surface((pw,ph)); popup.blit(wood,(0,0))
    pygame.draw.rect(popup, PRETO, popup.get_rect(),4)

    linhas = [
        "Você acorda no seu quarto após",
        "uma longa noite de sono, devido",
        "a uma feijoada na casa da sua vó",
        "você acorda 7h30 extremamente",
        "atrasado para a primeira aula.",
        "Saia do seu quarto para ir para a aula."
    ]
    for i, l in enumerate(linhas):
        txt = render_text_with_border(l, BRANCO, PRETO, 2)
        popup.blit(txt, (20, 20 + i*(FONT_SIZE+4)))

    rect = popup.get_rect(center=(LARGURA//2, ALTURA//2))
    espera = True
    while espera:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN): espera=False

        tela.blit(bg_quarto,(0,0))
        overlay = pygame.Surface((LARGURA,ALTURA), pygame.SRCALPHA)
        overlay.fill((0,0,0,150)); tela.blit(overlay,(0,0))
        tela.blit(popup, rect.topleft)
        pygame.display.flip()
        clock.tick(60)

# -------------- MAIN --------------
def main():
    show_intro()

    animations = load_animation_frames("animacoes", 0.45)
    jogador    = Jogador(animations)

    # paredes
    WALL = 10
    wall_obstaculos = [
        Obstaculo(0,0,LARGURA,WALL),
        Obstaculo(0,ALTURA-WALL,LARGURA,WALL),
        Obstaculo(0,0,WALL,ALTURA),
        Obstaculo(LARGURA-WALL,0,WALL,ALTURA)
    ]

    # zona de saída aumentada
    EXIT_W = int(0.1 * LARGURA)
    EXIT_H = 50
    exit_zone = pygame.Rect(int(0.4*LARGURA), ALTURA-EXIT_H, EXIT_W, EXIT_H)

    ajustar_posicao_inicial(jogador, wall_obstaculos)
    grupo = pygame.sprite.Group(jogador)

    asking_exit = False
    was_in_zone = False

    rodando = True
    while rodando:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if asking_exit and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s:
                    onibus.main(); return
                elif e.key == pygame.K_n:
                    asking_exit = False

        teclas = pygame.key.get_pressed()
        if not asking_exit:
            jogador.update(teclas, wall_obstaculos)
            in_zone = jogador.rect.colliderect(exit_zone)
            if in_zone and not was_in_zone:
                asking_exit = True
            was_in_zone = in_zone

        # desenha tudo
        tela.blit(bg_quarto, (0,0))
        for o in wall_obstaculos:
            tela.blit(o.image, o.rect)
        grupo.draw(tela)

        # popup de saída
        if asking_exit:
            pw,ph = 500,150
            wood = pygame.transform.scale(wood_tex,(pw,ph))
            popup = pygame.Surface((pw,ph)); popup.blit(wood,(0,0))
            pygame.draw.rect(popup, PRETO, popup.get_rect(),4)
            t1 = render_text_with_border("Quer sair do quarto?", BRANCO, PRETO, 2)
            t2 = render_text_with_border("S: Sim    N: Não", BRANCO, PRETO, 2)
            popup.blit(t1, ((pw-t1.get_width())//2,20))
            popup.blit(t2, ((pw-t2.get_width())//2,70))
            rect = popup.get_rect(center=(LARGURA//2, ALTURA//2))
            tela.blit(popup, rect.topleft)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
