import pygame
import sys
import os
import time
from typing import List, Tuple

pygame.init()

# -------------------- CONFIG --------------------
LARGURA = 1200
ALTURA = 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D - Lantern, Placas & Itens")

# Cores
BRANCO = (255, 255, 255)
CINZA = (100, 100, 100)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
AZUL = (50, 150, 255)
AMARELO = (240, 240, 0)

clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 24)

# -------------------- ASSETS HELPERS --------------------


def load_animation_frames(folder: str = "animacoes", scale_factor: float = 0.1) -> dict[str, List[pygame.Surface]]:
    """Carrega 16 quadros (frame_0.png ... frame_15.png) e devolve um dict separado por direcao."""
    frames: List[pygame.Surface] = []
    for i in range(16):
        path = os.path.join(folder, f"frame_{i}.png")
        img = pygame.image.load(path).convert_alpha()
        ow, oh = img.get_size()
        scaled = pygame.transform.scale(img, (int(ow * scale_factor), int(oh * scale_factor)))
        frames.append(scaled)
    return {
        "down": frames[0:4],
        "left": frames[8:12],
        "right": frames[12:16],
        "up": frames[4:8],
    }


def load_item_image(nome: str, tamanho: Tuple[int, int] = (40, 40)) -> pygame.Surface:
    """Tenta carregar uma imagem PNG para o item. Se nao existir, cria um placeholder."""
    arquivo = f"{nome.lower()}.png"
    caminho = os.path.join("itens", arquivo)
    if os.path.exists(caminho):
        img = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(img, tamanho)
    # placeholder
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    surf.fill(AMARELO)
    pygame.draw.rect(surf, PRETO, surf.get_rect(), 2)
    letra = fonte.render(nome[0].upper(), True, PRETO)
    letra_rect = letra.get_rect(center=surf.get_rect().center)
    surf.blit(letra, letra_rect)
    return surf

# -------------------- SPRITES --------------------


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


class Item(pygame.sprite.Sprite):
    """Representa um item coletável no mapa."""

    def __init__(self, x: int, y: int, nome: str):
        super().__init__()
        self.nome: str = nome
        self.image = load_item_image(nome, tamanho=(40, 40))
        self.rect = self.image.get_rect(center=(x, y))


class Jogador(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.current_direction = "down"
        self.frame_index: float = 0.0
        self.frame_speed: float = 0.15
        self.image = animations[self.current_direction][0]
        self.rect = self.image.get_rect(center=(LARGURA // 2, ALTURA // 2))
        self.velocidade = 5
        self.inventario: List[Tuple[str, pygame.Surface]] = []  # (nome, icon)

    # --------------------------------------------------
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

        # colisao com obstaculos
        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                self.rect = old_rect
                break

        # mantem dentro da tela
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        # animacao
        if movendo:
            self.frame_index = (self.frame_index + self.frame_speed) % len(self.animations[self.current_direction])
        else:
            self.frame_index = 0
        self.image = self.animations[self.current_direction][int(self.frame_index)]

    # --------------------------------------------------
    def coletar_item(self, item: Item):
        """Adiciona o item ao inventário se ainda não possuir."""
        if not any(nome == item.nome for nome, _ in self.inventario):
            self.inventario.append((item.nome, item.image))

# -------------------- UTILS --------------------


def ajustar_posicao_inicial(jogador: Jogador, obstaculos: List[Obstaculo]):
    """Evita que o jogador nasça dentro de um obstáculo."""
    while any(jogador.rect.colliderect(o.rect) for o in obstaculos):
        jogador.rect.y -= jogador.velocidade
        if jogador.rect.top <= 0:
            jogador.rect.top = 0
            jogador.rect.x += jogador.velocidade
            if jogador.rect.right >= LARGURA:
                jogador.rect.right = LARGURA
                break


def desenhar_inventario_top_right(jogador: Jogador):
    """Mostra os itens coletados empilhados no canto superior direito, com a imagem imediatamente à direita do texto."""
    padding = 10
    x_cursor = LARGURA - padding
    y_cursor = padding
    for nome, icon in reversed(jogador.inventario):  # últimos no topo
        texto = fonte.render(nome, True, PRETO)
        texto_rect = texto.get_rect(topleft=(x_cursor - texto.get_width() - icon.get_width() - padding, y_cursor))
        icon_rect = icon.get_rect(topleft=(texto_rect.right + padding, y_cursor))
        tela.blit(texto, texto_rect)
        tela.blit(icon, icon_rect)
        y_cursor += max(icon_rect.height, texto_rect.height) + padding  # espaço entre itens

# -------------------- MAIN GAME LOOP --------------------


def main():
    animations = load_animation_frames("animacoes", scale_factor=0.15)
    jogador = Jogador(animations)

    last_transition_time = 0.0
    transition_cooldown = 1.0

    lendo_placa = False
    texto_da_placa = ""

    item_alvo: Item | None = None

    fases = [
        {
            "obstaculos": [Obstaculo(300, 200, 200, 50)],
            "placas": [Placa(600, 300, 40, 40, "Bem-vindo à portaria!")],
            "itens": [Item(400, 400, "Chave")],
            "area_transicao": pygame.Rect(0, 0, LARGURA, 5),
            "transicao_direcao": "top",
            "fundo": pygame.image.load("portaria.png").convert()
        },
        {
            "obstaculos": [Obstaculo(100, 100, 400, 50)],
            "placas": [Placa(500, 600, 40, 40, "Aqui é o jardim central.")],
            "itens": [Item(800, 500, "Mapa")],
            "area_transicao": pygame.Rect(0, ALTURA - 5, LARGURA, 5),
            "transicao_direcao": "bottom",
            "fundo": pygame.image.load("bolajardim.png").convert()
        }
    ]

    fase_atual = 0
    grupo_jogador = pygame.sprite.Group(jogador)
    ajustar_posicao_inicial(jogador, fases[0]["obstaculos"])

    placa_proxima: Placa | None = None

    rodando = True
    while rodando:
        clock.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            # --------- interação de placas ---------
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_e:
                if placa_proxima:  # ler a placa
                    lendo_placa = True
                    texto_da_placa = placa_proxima.texto
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                lendo_placa = False
            # --------- coletar itens ---------
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_f:
                if item_alvo is not None:
                    jogador.coletar_item(item_alvo)
                    # remove do grupo da fase
                    fases[fase_atual]["itens"].remove(item_alvo)
                    item_alvo.kill()
                    item_alvo = None

        # ------------ ATUALIZAÇÃO DA FASE -----------
        fase = fases[fase_atual]
        grupo_obstaculos = pygame.sprite.Group(*fase["obstaculos"])
        grupo_placas = pygame.sprite.Group(*fase["placas"])
        grupo_itens = pygame.sprite.Group(*fase["itens"])

        teclas = pygame.key.get_pressed()
        if not lendo_placa:
            jogador.update(teclas, fase["obstaculos"])

        # ------------ TRANSIÇÃO DE FASE -------------
        agora = time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and (agora - last_transition_time > transition_cooldown):
            last_transition_time = agora
            x0, y0 = jogador.rect.center
            dir0 = fase["transicao_direcao"]
            fase_atual = (fase_atual + 1) % len(fases)
            nova = fases[fase_atual]
            # teleporta para o lado oposto
            if dir0 == "top":
                jogador.rect.midtop = (x0, ALTURA - jogador.rect.height)
            elif dir0 == "bottom":
                jogador.rect.midbottom = (x0, 0)
            elif dir0 == "left":
                jogador.rect.midleft = (LARGURA - jogador.rect.width, y0)
            elif dir0 == "right":
                jogador.rect.midright = (0, y0)
            ajustar_posicao_inicial(jogador, nova["obstaculos"])

        # ------------ DESENHO -----------------------
        tela.blit(fase["fundo"], (0, 0))
        grupo_obstaculos.draw(tela)
        grupo_placas.draw(tela)
        grupo_itens.draw(tela)
        grupo_jogador.draw(tela)
        pygame.draw.rect(tela, AZUL, fase["area_transicao"], 2)

        # --------- PROXIMIDADE DE PLACAS -----------
        placa_proxima = None
        for placa in grupo_placas:
            if jogador.rect.colliderect(placa.rect.inflate(40, 40)):
                placa_proxima = placa
                break

        if placa_proxima and not lendo_placa:
            texto = fonte.render("Pressione E para ler a placa", True, PRETO)
            tela.blit(texto, (jogador.rect.x - 40, jogador.rect.y - 30))

        # --------- PROXIMIDADE DE ITENS ------------
        item_alvo = None
        for item in grupo_itens:
            if jogador.rect.colliderect(item.rect.inflate(40, 40)):
                item_alvo = item
                break

        if item_alvo:
            texto = fonte.render("Pressione F para coletar", True, PRETO)
            tela.blit(texto, (jogador.rect.x - 40, jogador.rect.y - 50))

        # --------- CAIXA DE TEXTO DA PLACA ---------
        if lendo_placa:
            caixa = pygame.Rect(100, 600, 1000, 150)
            pygame.draw.rect(tela, BRANCO, caixa)
            pygame.draw.rect(tela, PRETO, caixa, 3)
            linhas = texto_da_placa.split("\n")
            for i, linha in enumerate(linhas):
                render = fonte.render(linha, True, PRETO)
                tela.blit(render, (120, 620 + i * 30))

        # --------- HUD DE INVENTARIO ---------------
        desenhar_inventario_top_right(jogador)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
