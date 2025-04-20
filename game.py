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
pygame.display.set_caption("Jogo 2D - Com Placas Interativas")

# Cores
BRANCO = (255, 255, 255)
CINZA = (100, 100, 100)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)

clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 24)

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

# -------------- CLASSES DO JOGO --------------

class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(CINZA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Placa(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, texto):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(VERDE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.texto = texto

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

# -------------- MAIN --------------

def main():
    animations = load_animation_frames("animacoes", scale_factor=0.15)
    jogador = Jogador(animations)

    last_transition_time = 0
    transition_cooldown = 1.0
    lendo_placa = False
    texto_da_placa = ""

    fases = [
        {
            "obstaculos": [Obstaculo(300, 200, 200, 50)],
            "placas": [Placa(600, 300, 40, 40, "Bem-vindo à portaria!")],
            "area_transicao": pygame.Rect(0, 0, 1200, 5),
            "transicao_direcao": "top",
            "fundo": pygame.image.load("portaria.png").convert()
        },
        {
            "obstaculos": [Obstaculo(100, 100, 400, 50)],
            "placas": [Placa(500, 600, 40, 40, "Aqui é o jardim central.")],
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
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_e:
                if placa_proxima:
                    lendo_placa = True
                    texto_da_placa = placa_proxima.texto
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                lendo_placa = False

        fase = fases[fase_atual]
        grupo_obstaculos = pygame.sprite.Group(fase["obstaculos"])
        grupo_placas = pygame.sprite.Group(fase["placas"])

        teclas = pygame.key.get_pressed()
        if not lendo_placa:
            jogador.update(teclas, grupo_obstaculos.sprites())

        tempo_atual = time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and (tempo_atual - last_transition_time > transition_cooldown):
            last_transition_time = tempo_atual
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

        tela.blit(fase["fundo"], (0, 0))
        grupo_obstaculos.draw(tela)
        grupo_placas.draw(tela)
        grupo_jogador.draw(tela)
        pygame.draw.rect(tela, (0, 255, 0), fase["area_transicao"], 2)

        # Verifica se há placa próxima
        placa_proxima = None
        for placa in grupo_placas:
            if jogador.rect.colliderect(placa.rect.inflate(40, 40)):
                placa_proxima = placa
                break

        # Exibe prompt
        if placa_proxima and not lendo_placa:
            texto = fonte.render("Pressione E para ler a placa", True, PRETO)
            tela.blit(texto, (jogador.rect.x - 40, jogador.rect.y - 30))

        # Exibe janela de texto da placa
        if lendo_placa:
            caixa = pygame.Rect(100, 600, 1000, 150)
            pygame.draw.rect(tela, BRANCO, caixa)
            pygame.draw.rect(tela, PRETO, caixa, 3)
            linhas = texto_da_placa.split("\n")
            for i, linha in enumerate(linhas):
                texto_render = fonte.render(linha, True, PRETO)
                tela.blit(texto_render, (120, 620 + i * 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
