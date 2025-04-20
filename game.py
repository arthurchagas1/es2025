import pygame
import sys
import os
import time
from typing import List

pygame.init()

# Configurações de tela
LARGURA = 1200
ALTURA = 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D - Troca de Fase com Lantern")

# Cores
BRANCO = (255, 255, 255)
CINZA = (100, 100, 100)

clock = pygame.time.Clock()

# -------------- CARREGANDO AS IMAGENS ANIMADAS --------------

def load_animation_frames(folder="animacoes", scale_factor=0.1):
    frames = []
    for i in range(16):
        path = os.path.join(folder, f"frame_{i}.png")
        img = pygame.image.load(path).convert_alpha()
        ow, oh = img.get_size()
        scaled = pygame.transform.scale(img, (int(ow * scale_factor), int(oh * scale_factor)))
        frames.append(scaled)

    return {
        "down":  frames[0:4],
        "left":  frames[8:12],
        "right": frames[12:16],
        "up":    frames[4:8],
    }

# -------------- CLASSES --------------

class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(CINZA)
        self.rect = self.image.get_rect(topleft=(x, y))

class Jogador(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.current_direction = "down"
        self.frame_index = 0
        self.frame_speed = 0.15
        self.image = animations[self.current_direction][0]
        self.rect = self.image.get_rect(center=(LARGURA // 2, ALTURA // 2))
        self.velocidade = 5

    def update(self, teclas, obstaculos: List[Obstaculo]):
        old_rect = self.rect.copy()
        movendo = False

        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidade
            self.current_direction = "left"
            movendo = True
        elif teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidade
            self.current_direction = "right"
            movendo = True
        elif teclas[pygame.K_UP]:
            self.rect.y -= self.velocidade
            self.current_direction = "up"
            movendo = True
        elif teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidade
            self.current_direction = "down"
            movendo = True

        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                self.rect = old_rect
                break

        # Limita o jogador dentro da tela
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        if movendo:
            self.frame_index = (self.frame_index + self.frame_speed) % len(self.animations[self.current_direction])
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

# -------------- MAIN GAME LOOP --------------

def main():
    animations = load_animation_frames("animacoes", scale_factor=0.15)
    jogador = Jogador(animations)

    last_transition_time = 0.0
    transition_cooldown = 1.0  # segundos

    fases = [
        {
            "obstaculos": [Obstaculo(300, 200, 200, 50)],
            "area_transicao": pygame.Rect(0, 0, LARGURA, 5),
            "transicao_direcao": "top",
            "fundo": pygame.image.load("portaria.png").convert()
        },
        {
            "obstaculos": [Obstaculo(100, 100, 400, 50)],
            "area_transicao": pygame.Rect(0, ALTURA-5, LARGURA, 5),
            "transicao_direcao": "bottom",
            "fundo": pygame.image.load("bolajardim.png").convert()
        }
    ]

    fase_atual = 0
    grupo_jogador = pygame.sprite.Group(jogador)

    ajustar_posicao_inicial(jogador, fases[0]["obstaculos"])

    rodando = True
    while rodando:
        clock.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        fase = fases[fase_atual]
        grupo_obstaculos = pygame.sprite.Group(*fase["obstaculos"])

        teclas = pygame.key.get_pressed()
        jogador.update(teclas, fase["obstaculos"])

        # Transição de fase
        agora = time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and (agora - last_transition_time > transition_cooldown):
            last_transition_time = agora
            x0, y0 = jogador.rect.center
            dir0 = fase["transicao_direcao"]

            fase_atual = (fase_atual + 1) % len(fases)
            nova = fases[fase_atual]

            if dir0 == "top":
                y_new = ALTURA - jogador.rect.height
                jogador.rect.midtop = (x0, y_new)
            elif dir0 == "bottom":
                jogador.rect.midbottom = (x0, 0)
            elif dir0 == "left":
                jogador.rect.midleft = (LARGURA - jogador.rect.width, y0)
            elif dir0 == "right":
                jogador.rect.midright = (0, y0)

            ajustar_posicao_inicial(jogador, nova["obstaculos"])

        # Desenha cena
        tela.blit(fase["fundo"], (0, 0))
        grupo_obstaculos.draw(tela)
        grupo_jogador.draw(tela)
        pygame.draw.rect(tela, (0,255,0), fase["area_transicao"], 2)  # debug

        # Lantern: tudo fora do raio fica preto
        light = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        light.fill((0, 0, 0, 255))
        radius = 200
        max_dark = 180
        cx, cy = jogador.rect.center
        for r in range(radius, 0, -1):
            alpha = int(max_dark * (r / radius))
            pygame.draw.circle(light, (0, 0, 0, alpha), (cx, cy), r)

        tela.blit(light, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()