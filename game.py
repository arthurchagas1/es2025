import pygame
import sys
import os

pygame.init()

# Configurações de tela
LARGURA = 1200
ALTURA = 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D - Personagem Animado (10x Menor)")

# Cores
BRANCO = (255, 255, 255)
CINZA = (100, 100, 100)

clock = pygame.time.Clock()

# -------------- CARREGANDO AS IMAGENS ANIMADAS --------------

def load_animation_frames(folder="animacoes", scale_factor=0.1):
    """
    Carrega os 16 frames salvos na pasta 'animacoes', redimensiona cada um deles para
    que o personagem seja 10x menor e os organiza por direção.
    
    Assumindo que a organização seja:
      - Linha 0: Movimento para "baixo" (frames 0 a 3)
      - Linha 1: Movimento para "esquerda" (frames 4 a 7)
      - Linha 2: Movimento para "direita" (frames 8 a 11)
      - Linha 3: Movimento para "cima" (frames 12 a 15)
    """
    frames = []
    for i in range(16):
        path = os.path.join(folder, f"frame_{i}.png")
        img = pygame.image.load(path).convert_alpha()
        # Redimensiona a imagem para 10x menor
        orig_width, orig_height = img.get_size()
        scaled_img = pygame.transform.scale(img, (int(orig_width * scale_factor), int(orig_height * scale_factor)))
        frames.append(scaled_img)

    frames_down  = frames[0:4]    # linha 0: baixo
    frames_left  = frames[8:12]    # linha 1: esquerda
    frames_right = frames[12:16]   # linha 2: direita
    frames_up    = frames[4:8]  # linha 3: cima

    return {
        "down":  frames_down,
        "left":  frames_left,
        "right": frames_right,
        "up":    frames_up
    }

# -------------- CRIAÇÃO DOS OBSTÁCULOS --------------

class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(CINZA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

obstaculo1 = Obstaculo(300, 200, 200, 50)
obstaculo2 = Obstaculo(700, 500, 50, 200)
obstaculo3 = Obstaculo(500, 300, 150, 150)
grupo_obstaculos = pygame.sprite.Group(obstaculo1, obstaculo2, obstaculo3)

# -------------- CRIAÇÃO DO JOGADOR ANIMADO --------------

class Jogador(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.current_direction = "down"  # direção inicial
        self.frame_index = 0
        self.frame_speed = 0.15  # velocidade de troca de frames
        self.image = self.animations[self.current_direction][int(self.frame_index)]
        self.rect = self.image.get_rect(center=(LARGURA // 2, ALTURA // 2))
        self.velocidade = 5

    def update(self, teclas, obstaculos):
        # Salva a posição anterior, caso haja colisão
        pos_antiga = self.rect.copy()
        movendo = False

        # Detecta movimento e altera a direção
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

        # Verifica colisão com obstáculos
        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                self.rect = pos_antiga
                break

        # Impede que o personagem saia das bordas da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTURA:
            self.rect.bottom = ALTURA

        # Atualiza o frame para animar se estiver se movendo
        if movendo:
            self.frame_index += self.frame_speed
            if self.frame_index >= len(self.animations[self.current_direction]):
                self.frame_index = 0
        else:
            # Se parado, retorna ao primeiro frame da direção
            self.frame_index = 0

        # Atualiza a imagem com o frame atual
        self.image = self.animations[self.current_direction][int(self.frame_index)]

def ajustar_posicao_inicial(jogador, obstaculos):
    """
    Se o jogador nascer em cima de algum obstáculo, move-o para que não haja colisão.
    """
    while any(jogador.rect.colliderect(obs.rect) for obs in obstaculos):
        jogador.rect.y -= jogador.velocidade
        if jogador.rect.top <= 0:
            jogador.rect.top = 0
            jogador.rect.x += jogador.velocidade
            if jogador.rect.right >= LARGURA:
                jogador.rect.right = LARGURA
                break

def main():
    # Carrega as animações com o scale_factor definido para reduzir 10x
    animations = load_animation_frames("animacoes", scale_factor=0.15)
    jogador = Jogador(animations)
    ajustar_posicao_inicial(jogador, grupo_obstaculos.sprites())
    grupo_jogador = pygame.sprite.Group(jogador)

    rodando = True
    while rodando:
        clock.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        teclas = pygame.key.get_pressed()
        jogador.update(teclas, grupo_obstaculos.sprites())

        tela.fill(BRANCO)
        grupo_obstaculos.draw(tela)
        grupo_jogador.draw(tela)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
