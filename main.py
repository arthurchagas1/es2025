import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jogo de Plataforma com Câmera e Obstáculos")

# Definindo dimensões do mundo (maior que a tela para demonstrar o movimento da câmera)
WORLD_WIDTH, WORLD_HEIGHT = 2000, 600

# Definição de cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
AZUL = (50, 50, 255)
VERMELHO = (255, 0, 0)

clock = pygame.time.Clock()

# Classe que representa o jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, obstacles):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(AZUL)
        self.rect = self.image.get_rect()
        # Posição inicial dentro do mundo
        self.rect.center = (100, WORLD_HEIGHT - 100)
        # Variáveis de movimento e física
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_strength = -15
        self.obstacles = obstacles

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        # Limitar o jogador para não sair do mundo horizontalmente
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WORLD_WIDTH:
            self.rect.right = WORLD_WIDTH

        # Aplicação da gravidade
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Colisão com o "chão" do mundo
        floor_y = WORLD_HEIGHT - 50  # O chão fica a 50 pixels da borda inferior do mundo
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
            self.vel_y = 0

        # Colisão com obstáculos (apenas para colisão pela parte superior)
        for obstacle in self.obstacles:
            if self.rect.colliderect(obstacle.rect):
                # Se o jogador estiver descendo e colidir por cima do obstáculo
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= obstacle.rect.top:
                    self.rect.bottom = obstacle.rect.top
                    self.vel_y = 0

    def jump(self):
        # Permite pular se estiver no chão ou em cima de um obstáculo
        floor_y = WORLD_HEIGHT - 50
        if self.rect.bottom >= floor_y or any(self.rect.colliderect(o.rect) for o in self.obstacles):
            self.vel_y = self.jump_strength

# Classe que representa um obstáculo (plataforma)
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(VERMELHO)
        self.rect = self.image.get_rect(topleft=(x, y))

# Criação do grupo de obstáculos e adição de alguns obstáculos
obstacles = pygame.sprite.Group()
# Exemplo de plataformas em posições variadas no mundo
obstacle1 = Obstacle(400, WORLD_HEIGHT - 150, 150, 20)
obstacle2 = Obstacle(800, WORLD_HEIGHT - 200, 200, 20)
obstacle3 = Obstacle(1300, WORLD_HEIGHT - 250, 150, 20)
obstacles.add(obstacle1, obstacle2, obstacle3)

# Criação do jogador e grupo de sprites (incluindo obstáculos e jogador)
all_sprites = pygame.sprite.Group()
player = Player(obstacles)
all_sprites.add(player)
# Adiciona obstáculos ao grupo geral para facilitar na hora do desenho
all_sprites.add(obstacles)

def get_camera_offset(target_rect):
    """
    Calcula o deslocamento (offset) da câmera com base na posição do alvo,
    de modo que o personagem fique centralizado na tela.
    O offset é limitado para não mostrar áreas fora do mundo.
    """
    offset_x = target_rect.centerx - SCREEN_WIDTH // 2
    offset_y = target_rect.centery - SCREEN_HEIGHT // 2

    # Limita o offset para que a câmera não mostre além dos limites do mundo
    offset_x = max(0, min(offset_x, WORLD_WIDTH - SCREEN_WIDTH))
    offset_y = max(0, min(offset_y, WORLD_HEIGHT - SCREEN_HEIGHT))
    return offset_x, offset_y

def draw():
    # Calcula o offset da câmera com base na posição do jogador
    camera_offset = get_camera_offset(player.rect)
    screen.fill(BRANCO)
    
    # Desenha o "chão" do mundo
    floor_rect = pygame.Rect(0 - camera_offset[0], (WORLD_HEIGHT - 50) - camera_offset[1],
                             WORLD_WIDTH, 50)
    pygame.draw.rect(screen, VERDE, floor_rect)

    # Desenha todos os sprites ajustando pela posição da câmera
    for sprite in all_sprites:
        adjusted_rect = sprite.rect.copy()
        adjusted_rect.x -= camera_offset[0]
        adjusted_rect.y -= camera_offset[1]
        screen.blit(sprite.image, adjusted_rect)

    pygame.display.flip()

# Loop principal do jogo
running = True
while running:
    clock.tick(60)  # Define 60 FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Detecta o pulo quando a tecla de espaço é pressionada
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
    
    # Atualiza todos os sprites (o player é que tem a lógica de movimento e colisão)
    all_sprites.update()
    
    # Atualiza o desenho na tela com base na posição da câmera
    draw()

pygame.quit()
sys.exit()
