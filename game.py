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
pygame.display.set_caption("Jogo 2D - Com Lantern e Placas")

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
    transition_cooldown = 1.0
    lendo_placa = False
    texto_da_placa = ""

    fases = [
        {
            "obstaculos": [Obstaculo(300, 200, 200, 50)],
            "placas": [Placa(600, 300, 40, 40, "Bem-vindo à portaria!")],
            "area_transicao": pygame.Rect(0, 0, LARGURA, 5),
            "transicao_direcao": "top",
            "fundo": pygame.image.load("portaria.png").convert()
        },
        {
            "obstaculos": [Obstaculo(100, 100, 400, 50)],
            "placas": [Placa(500, 600, 40, 40, "Aqui é o jardim central.")],
            "area_transicao": pygame.Rect(0, ALTURA - 5, LARGURA, 5),
            "transicao_direcao": "bottom",
            "fundo": pygame.image.load("bolajardim.png").convert()
        }
    ]

    fase_atual = 0
    grupo_jogador = pygame.sprite.Group(jogador)
    ajustar_posicao_inicial(jogador, fases[0]["obstaculos"])

    placa_proxima = None
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
        grupo_obstaculos = pygame.sprite.Group(*fase["obstaculos"])
        grupo_placas = pygame.sprite.Group(*fase["placas"])
        teclas = pygame.key.get_pressed()
        if not lendo_placa:
            jogador.update(teclas, fase["obstaculos"])

        agora = time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and (agora - last_transition_time > transition_cooldown):
            last_transition_time = agora
            x0, y0 = jogador.rect.center
            dir0 = fase["transicao_direcao"]
            fase_atual = (fase_atual + 1) % len(fases)
            nova = fases[fase_atual]
            if dir0 == "top":
                jogador.rect.midtop = (x0, ALTURA - jogador.rect.height)
            elif dir0 == "bottom":
                jogador.rect.midbottom = (x0, 0)
            elif dir0 == "left":
                jogador.rect.midleft = (LARGURA - jogador.rect.width, y0)
            elif dir0 == "right":
                jogador.rect.midright = (0, y0)
            ajustar_posicao_inicial(jogador, nova["obstaculos"])

        tela.blit(fase["fundo"], (0, 0))
        grupo_obstaculos.draw(tela)
        grupo_placas.draw(tela)
        grupo_jogador.draw(tela)
        pygame.draw.rect(tela, (0, 255, 0), fase["area_transicao"], 2)

        # Interação com placas
        placa_proxima = None
        for placa in grupo_placas:
            if jogador.rect.colliderect(placa.rect.inflate(40, 40)):
                placa_proxima = placa
                break

        if placa_proxima and not lendo_placa:
            texto = fonte.render("Pressione E para ler a placa", True, PRETO)
            tela.blit(texto, (jogador.rect.x - 40, jogador.rect.y - 30))

        if lendo_placa:
            caixa = pygame.Rect(100, 600, 1000, 150)
            pygame.draw.rect(tela, BRANCO, caixa)
            pygame.draw.rect(tela, PRETO, caixa, 3)
            linhas = texto_da_placa.split("\\n")
            for i, linha in enumerate(linhas):
                render = fonte.render(linha, True, PRETO)
                tela.blit(render, (120, 620 + i * 30))

        # Efeito da lanterna
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