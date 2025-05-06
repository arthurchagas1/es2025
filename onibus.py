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
        self.rect              = self.image.get_rect(center=(LARGURA//2, ALTURA//2))
        self.velocidade        = 5

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

        # mantém dentro das bordas superior, inferior e direita
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        # animação
        if mov:
            seq = self.animations[self.current_direction]
            self.frame_index = (self.frame_index + self.frame_speed) % len(seq)
        else:
            self.frame_index = 0
        self.image = self.animations[self.current_direction][int(self.frame_index)]

def main():
    # carrega fundo e personagem
    fundo = pygame.transform.scale(
        pygame.image.load("onibus.png").convert(),
        (LARGURA, ALTURA)
    )
    animations = load_animation_frames("animacoes", scale_factor=0.45)
    jogador    = Jogador(animations)
    grupo = pygame.sprite.Group(jogador)

    asking_exit = False

    rodando = True
    while rodando:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False

            # se estiver no prompt de saída, espera S ou N
            if asking_exit and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s:      # 'S' para Sim
                    game.main()
                    return
                elif e.key == pygame.K_n:    # 'N' para Não
                    asking_exit = False

        if not asking_exit:
            teclas = pygame.key.get_pressed()
            jogador.update(teclas)
            # se tentar sair para a esquerda
            if jogador.rect.left <= 0:
                # trava na borda e abre prompt
                jogador.rect.left = 0
                asking_exit = True

        # desenha cenário e jogador
        tela.blit(fundo, (0, 0))
        grupo.draw(tela)

        # se no prompt, desenha a janelinha
        if asking_exit:
            w, h = 400, 200
            popup = pygame.Surface((w, h))
            popup.fill(BRANCO)
            rect = popup.get_rect(center=(LARGURA//2, ALTURA//2))
            pygame.draw.rect(popup, PRETO, popup.get_rect(), 2)
            txt1 = fonte.render("Deseja ir para a UFMG?", True, PRETO)
            txt2 = fonte.render("S: Sim    N: Não", True, PRETO)
            popup.blit(txt1, ((w-txt1.get_width())//2, 60))
            popup.blit(txt2, ((w-txt2.get_width())//2, 120))
            tela.blit(popup, rect.topleft)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
