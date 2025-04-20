import pygame
import sys
import os
from typing import List
import time


pygame.init()

# Configurações de tela
LARGURA = 1200
ALTURA = 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D - Troca de Fase com Transição Suave")

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
        orig_width, orig_height = img.get_size()
        scaled_img = pygame.transform.scale(img, (int(orig_width * scale_factor), int(orig_height * scale_factor)))
        frames.append(scaled_img)

    frames_down  = frames[0:4]    
    frames_left  = frames[8:12]   
    frames_right = frames[12:16]  
    frames_up    = frames[4:8]    

    return {
        "down":  frames_down,
        "left":  frames_left,
        "right": frames_right,
        "up":    frames_up
    }

# -------------- OBSTÁCULO --------------

class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(CINZA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# -------------- JOGADOR --------------

class Jogador(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.current_direction = "down"
        self.frame_index = 0
        self.frame_speed = 0.15
        self.image = self.animations[self.current_direction][int(self.frame_index)]
        self.rect = self.image.get_rect(center=(LARGURA // 2, ALTURA // 2))
        self.velocidade = 5

    def update(self, teclas, obstaculos):
        pos_antiga = self.rect.copy()
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
                self.rect = pos_antiga
                break

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTURA:
            self.rect.bottom = ALTURA

        if movendo:
            self.frame_index += self.frame_speed
            if self.frame_index >= len(self.animations[self.current_direction]):
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = self.animations[self.current_direction][int(self.frame_index)]

def ajustar_posicao_inicial(jogador, obstaculos):
    while any(jogador.rect.colliderect(obs.rect) for obs in obstaculos):
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

    last_transition_time = 0  # controla cooldown
    transition_cooldown = 1.0  # segundos


    fases = [
        {
            "obstaculos": [Obstaculo(300, 200, 200, 50)],
            "area_transicao": pygame.Rect(0, 0, 1200, 5),
            "transicao_direcao": "top",
            "fundo": pygame.image.load("portaria.png").convert()
        },
        {
            "obstaculos": [Obstaculo(100, 100, 400, 50)],
            "area_transicao": pygame.Rect(0, 795, 1200, 5),
            "transicao_direcao": "bottom",
            "fundo": pygame.image.load("bolajardim.png").convert()
        }
    ]

    fase_atual = 0
    grupo_jogador = pygame.sprite.Group(jogador)

    rodando = True
    while rodando:
        clock.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        fase = fases[fase_atual]
        grupo_obstaculos = pygame.sprite.Group(fase["obstaculos"])

        teclas = pygame.key.get_pressed()
        jogador.update(teclas, grupo_obstaculos.sprites())

        # Verifica transição de fase
        tempo_atual = time.time()

        if jogador.rect.colliderect(fase["area_transicao"]) and (tempo_atual - last_transition_time > transition_cooldown):
            last_transition_time = tempo_atual  # aplica o cooldown

            x_atual = jogador.rect.centerx
            y_atual = jogador.rect.centery
            direcao = fase["transicao_direcao"]

            fase_atual = (fase_atual + 1) % len(fases)
            nova_fase = fases[fase_atual]

            if direcao == "top":
                nova_y = ALTURA - jogador.rect.height
                jogador.rect.midtop = (x_atual, nova_y)
            elif direcao == "bottom":
                nova_y = 0
                jogador.rect.midbottom = (x_atual, nova_y)
            elif direcao == "left":
                nova_x = LARGURA - jogador.rect.width
                jogador.rect.midleft = (nova_x, y_atual)
            elif direcao == "right":
                nova_x = 0
                jogador.rect.midright = (nova_x, y_atual)

            ajustar_posicao_inicial(jogador, nova_fase["obstaculos"])


        # Desenha fundo, obstáculos e jogador
        tela.blit(fase["fundo"], (0, 0))
        grupo_obstaculos.draw(tela)
        grupo_jogador.draw(tela)

        # Opcional: desenha área de transição para debug
        pygame.draw.rect(tela, (0, 255, 0), fase["area_transicao"], 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
