import pygame
import sys

# Inicialização do pygame
pygame.init()

# Configurações da janela do jogo
LARGURA = 1200
ALTURA = 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D Estilo Undertale - Principal")

# Definição de cores
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
CINZA = (100, 100, 100)

# Controle de FPS
clock = pygame.time.Clock()

# Classe do obstáculo
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(CINZA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Grupo de obstáculos
grupo_obstaculos = pygame.sprite.Group()
obstaculo1 = Obstaculo(300, 200, 200, 50)
obstaculo2 = Obstaculo(700, 500, 50, 200)
obstaculo3 = Obstaculo(500, 300, 150, 150)
grupo_obstaculos.add(obstaculo1, obstaculo2, obstaculo3)

# Classe do jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Cria um sprite simples (pode ser substituído por uma imagem)
        self.image = pygame.Surface((40, 60))
        self.image.fill(VERMELHO)
        self.rect = self.image.get_rect()
        # Posiciona o jogador inicialmente no centro da tela
        self.rect.center = (LARGURA // 2, ALTURA // 2)
        self.velocidade = 5

    def update(self, teclas, obstaculos):
        # Guarda a posição anterior para reverter em caso de colisão
        pos_antiga = self.rect.copy()

        # Movimenta de acordo com as teclas pressionadas
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidade
        if teclas[pygame.K_UP]:
            self.rect.y -= self.velocidade
        if teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidade

        # Verifica colisões com os obstáculos e reverte a posição se necessário
        for obstaculo in obstaculos:
            if self.rect.colliderect(obstaculo.rect):
                self.rect = pos_antiga
                break

        # Impede que o jogador saia das bordas da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTURA:
            self.rect.bottom = ALTURA

# Função para ajustar a posição inicial do jogador se ele spawnar em cima de um obstáculo
def ajustar_posicao_inicial(jogador, obstaculos):
    # Enquanto houver colisão, move o jogador para cima. Se alcançar o topo, move para a direita.
    while any(jogador.rect.colliderect(obst.rect) for obst in obstaculos):
        jogador.rect.y -= jogador.velocidade
        if jogador.rect.top <= 0:
            jogador.rect.top = 0
            jogador.rect.x += jogador.velocidade
            if jogador.rect.right >= LARGURA:
                jogador.rect.right = LARGURA
                break

# Instancia o jogador e ajusta sua posição caso esteja sobre um obstáculo
jogador = Jogador()
ajustar_posicao_inicial(jogador, grupo_obstaculos.sprites())
todos_sprites = pygame.sprite.Group()
todos_sprites.add(jogador)

# Função principal do jogo
def main():
    rodando = True
    while rodando:
        # Limita a 60 FPS
        clock.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        # Captura o estado do teclado e atualiza o jogador
        teclas = pygame.key.get_pressed()
        jogador.update(teclas, grupo_obstaculos.sprites())

        # Redesenha a tela
        tela.fill(BRANCO)
        grupo_obstaculos.draw(tela)
        todos_sprites.draw(tela)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

# Executa o jogo somente se este arquivo for executado diretamente
if __name__ == "__main__":
    main()
