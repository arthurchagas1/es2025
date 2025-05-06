import pygame
import sys
import os
import time
from typing import List

pygame.init()

# -------------- PROPORÇÃO 16:9 --------------
LARGURA = 1280
ALTURA  = 720
tela    = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D - Com Placas (16:9)")

# Cores
BRANCO = (255, 255, 255)
CINZA  = (100, 100, 100)
PRETO  = (0, 0, 0)
VERDE  = (0, 255, 0)

clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 24)

# -------------- CARREGANDO AS IMAGENS ANIMADAS --------------
def load_animation_frames(folder="animacoes", scale_factor=0.45):
    frames = []
    for i in range(16):
        img = pygame.image.load(os.path.join(folder, f"frame_{i}.png")).convert_alpha()
        ow, oh = img.get_size()
        frames.append(pygame.transform.scale(img, (int(ow * scale_factor), int(oh * scale_factor))))
    return {
        "down":  frames[0:4],
        "left":  frames[8:12],
        "right": frames[12:16],
        "up":    frames[4:8],
    }

# -------------- CLASSES --------------
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(CINZA)
        self.rect  = self.image.get_rect(topleft=(x, y))

class Placa(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, texto):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(VERDE)
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.texto = texto

class Jogador(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()
        self.animations       = animations
        self.current_direction = "down"
        self.frame_index       = 0
        self.frame_speed       = 0.15
        self.image             = animations["down"][0]
        self.rect              = self.image.get_rect(center=(LARGURA//2, ALTURA//2))
        self.velocidade        = 5

    def update(self, teclas, obstaculos: List[Obstaculo]):
        old_rect = self.rect.copy()
        movendo  = False
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidade; self.current_direction = "left";  movendo = True
        elif teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidade; self.current_direction = "right"; movendo = True
        elif teclas[pygame.K_UP]:
            self.rect.y -= self.velocidade; self.current_direction = "up";    movendo = True
        elif teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidade; self.current_direction = "down";  movendo = True

        # colisão
        for o in obstaculos:
            if self.rect.colliderect(o.rect):
                self.rect = old_rect
                break
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        # animação
        if movendo:
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

# -------------- MAIN --------------
def main():
    animations = load_animation_frames("animacoes", scale_factor=0.45)
    jogador    = Jogador(animations)

    last_transition_time = 0.0
    transition_cooldown  = 1.0
    lendo_placa          = False
    texto_da_placa       = ""

    # Paredes do quarto (bordas)
    WALL = 10
    wall_obstaculos = [
        Obstaculo(0, 0, LARGURA, WALL),               # topo
        Obstaculo(0, ALTURA-WALL, LARGURA, WALL),     # base
        Obstaculo(0, 0, WALL, ALTURA),                # esquerda
        Obstaculo(LARGURA-WALL, 0, WALL, ALTURA)      # direita
    ]

    # Fases com background escalado para 16:9
    fases = [
        {
            "obstaculos": wall_obstaculos,
            "placas":     [],
            "area_transicao":    pygame.Rect(0, ALTURA-5, LARGURA, 5),
            "transicao_direcao": "bottom",
            "fundo": pygame.transform.scale(
                pygame.image.load("quarto.png").convert(),
                (LARGURA, ALTURA)
            )
        },
        {
            "obstaculos": [Obstaculo(300, 200, 200, 50)],
            "placas":     [Placa(600, 300, 40, 40, "Bem-vindo à portaria!")],
            "area_transicao":    pygame.Rect(0, 0, LARGURA, 5),
            "transicao_direcao": "top",
            "fundo": pygame.transform.scale(
                pygame.image.load("portaria.png").convert(),
                (LARGURA, ALTURA)
            )
        },
        {
            "obstaculos": [Obstaculo(100, 100, 400, 50)],
            "placas":     [Placa(500, 600, 40, 40, "Aqui é o jardim central.")],
            "area_transicao":    pygame.Rect(0, ALTURA-5, LARGURA, 5),
            "transicao_direcao": "bottom",
            "fundo": pygame.transform.scale(
                pygame.image.load("bolajardim.png").convert(),
                (LARGURA, ALTURA)
            )
        }
    ]

    fase_atual    = 0
    grupo_jogador = pygame.sprite.Group(jogador)
    ajustar_posicao_inicial(jogador, fases[0]["obstaculos"])

    placa_proxima = None
    rodando       = True
    while rodando:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e and placa_proxima:
                lendo_placa    = True
                texto_da_placa = placa_proxima.texto
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                lendo_placa = False

        fase = fases[fase_atual]
        obs  = pygame.sprite.Group(*fase["obstaculos"])
        placas = pygame.sprite.Group(*fase["placas"])
        teclas = pygame.key.get_pressed()
        if not lendo_placa:
            jogador.update(teclas, fase["obstaculos"])

        # Transição de fase
        agora = time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and (agora - last_transition_time > transition_cooldown):
            last_transition_time = agora
            x0, y0 = jogador.rect.center
            dir0   = fase["transicao_direcao"]
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

        # Desenho
        tela.blit(fase["fundo"], (0,0))
        obs.draw(tela)
        placas.draw(tela)
        grupo_jogador.draw(tela)

        # Debug: mostra area de transição
        pygame.draw.rect(tela, (0,255,0), fase["area_transicao"], 2)

        # Indicação de placa
        placa_proxima = None
        for p in placas:
            if jogador.rect.colliderect(p.rect.inflate(40,40)):
                placa_proxima = p
                break
        if placa_proxima and not lendo_placa:
            aviso = fonte.render("Pressione E para ler a placa", True, PRETO)
            tela.blit(aviso, (jogador.rect.x-40, jogador.rect.y-30))

        # Leitura de placa
        if lendo_placa:
            caixa = pygame.Rect(100, ALTURA-120, LARGURA-200, 100)
            pygame.draw.rect(tela, BRANCO, caixa)
            pygame.draw.rect(tela, PRETO, caixa, 3)
            for i, linha in enumerate(texto_da_placa.split("\\n")):
                render = fonte.render(linha, True, PRETO)
                tela.blit(render, (120, ALTURA-100 + i*30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
