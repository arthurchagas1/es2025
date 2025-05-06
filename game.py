import pygame
import sys
import os
import time
import random
from typing import List

pygame.init()
clock = pygame.time.Clock()

# --------------------- CONSTANTS ---------------------
LARGURA, ALTURA = 1200, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D – itens + quiz")

BRANCO = (255, 255, 255)
CINZA   = (100, 100, 100)
PRETO   = (0, 0, 0)
VERDE   = (0, 255, 0)
AZUL_CLARO = (150, 200, 255)

fonte   = pygame.font.SysFont("Arial", 24)

# --------------------- ASSET HELPERS -----------------
def load_animation_frames(folder="animacoes", scale_factor=0.15):
    frames = []
    for i in range(16):
        img = pygame.image.load(os.path.join(folder, f"frame_{i}.png")).convert_alpha()
        w, h = img.get_size()
        frames.append(pygame.transform.scale(img, (int(w*scale_factor), int(h*scale_factor))))
    return {"down":frames[0:4], "left":frames[8:12], "right":frames[12:16], "up":frames[4:8]}

def load_item_image(nome, size=(40, 40)):
    path = os.path.join("itens", f"{nome}.png")
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    # fallback placeholder
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((255, 255, 0))
    letter = fonte.render(nome[0].upper(), True, PRETO)
    r = letter.get_rect(center=(size[0]//2, size[1]//2))
    surf.blit(letter, r)
    return surf

def load_icon(path, fallback_color):
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (40, 40))
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf

# fallback check/X icons
ICON_OK   = load_icon("ok.png",   (0, 255, 0))
ICON_FAIL = load_icon("fail.png", (255, 0, 0))

# --------------------- SPRITE CLASSES ----------------
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(CINZA)
        self.rect = self.image.get_rect(topleft=(x, y))

class Placa(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, texto):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(VERDE)
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.texto = texto

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, nome):
        super().__init__()
        self.nome  = nome
        self.image = load_item_image(nome)
        self.rect  = self.image.get_rect(topleft=(x, y))

class Jogador(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.current_direction = "down"
        self.frame_index = 0
        self.frame_speed = 0.15
        self.image = animations["down"][0]
        self.rect  = self.image.get_rect(center=(LARGURA//2, ALTURA//2))
        self.velocidade = 5
        self.inventario: List[tuple[str, pygame.Surface]] = []

    def coletar_item(self, item: Item):
        for nome, _ in self.inventario:
            if nome == item.nome:
                return  # já tem
        self.inventario.append((item.nome, item.image))

    def update(self, teclas, obstaculos: List[Obstaculo]):
        old = self.rect.copy()
        movendo = False
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidade
            self.current_direction = "left"; movendo = True
        elif teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidade
            self.current_direction = "right"; movendo = True
        elif teclas[pygame.K_UP]:
            self.rect.y -= self.velocidade
            self.current_direction = "up"; movendo = True
        elif teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidade
            self.current_direction = "down"; movendo = True

        for o in obstaculos:
            if self.rect.colliderect(o.rect):
                self.rect = old; break
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        if movendo:
            self.frame_index = (self.frame_index + self.frame_speed) % len(self.animations[self.current_direction])
        else:
            self.frame_index = 0
        self.image = self.animations[self.current_direction][int(self.frame_index)]

# --------------------- INVENTORY HUD -----------------
def desenhar_inventario_top_right(surface, inventario):
    x = LARGURA - 50
    for nome, icon in reversed(inventario):
        surface.blit(icon, (x, 10))
        txt = fonte.render(nome, True, PRETO)
        surface.blit(txt, (x - txt.get_width() - 5, 15))
        x -= 120

# --------------------- QUIZ DATA ---------------------
class QuizQuestion:
    def __init__(self, pergunta, opcoes, correta_index):
        self.pergunta = pergunta
        self.opcoes   = opcoes
        self.correta  = correta_index

QUESTOES = [
    QuizQuestion("Quanto é 2 + 2?",
                 ["3", "4", "5", "22"], 1),
    QuizQuestion("Qual linguagem estamos usando?",
                 ["Java", "C++", "Python", "Ruby"], 2),
    QuizQuestion("Qual planeta é conhecido como o Planeta Vermelho?",
                 ["Terra", "Vênus", "Marte", "Júpiter"], 2),
    QuizQuestion("Quem pintou a Mona Lisa?",
                 ["Van Gogh", "Da Vinci", "Picasso", "Michelangelo"], 1),
    QuizQuestion("Em que continente fica o Brasil?",
                 ["África", "Europa", "Ásia", "América do Sul"], 3),
]

# --------------------- QUIZ LOOP ---------------------
def run_quiz(surface, font) -> bool:
    perguntas = random.sample(QUESTOES, 3)
    acertos   = 0

    for q in perguntas:
        selecionada = 0
        respondida  = False
        feedback_icon = None
        feedback_time = 0

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and not respondida:
                    if e.key in (pygame.K_UP, pygame.K_w):
                        selecionada = (selecionada - 1) % len(q.opcoes)
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        selecionada = (selecionada + 1) % len(q.opcoes)
                    elif e.key == pygame.K_RETURN:
                        respondida = True
                        correta = (selecionada == q.correta)
                        feedback_icon = ICON_OK if correta else ICON_FAIL
                        if correta: acertos += 1
                        feedback_time = time.time()

            # Draw quiz screen
            surface.fill((30, 30, 90))
            pergunta_render = font.render(q.pergunta, True, BRANCO)
            surface.blit(pergunta_render, (60, 80))

            for i, opcao in enumerate(q.opcoes):
                y = 200 + i*60
                if i == selecionada:
                    pygame.draw.rect(surface, AZUL_CLARO, (50, y-5, 700, 40))
                txt = font.render(opcao, True, BRANCO)
                surface.blit(txt, (60, y))
            if respondida:
                surface.blit(feedback_icon, (800, 200 + selecionada*60))
                if time.time() - feedback_time >= 1.0:
                    break

            pygame.display.flip()
            clock.tick(60)

    # Result screen
    passou = acertos >= 2
    msg = "Parabéns! Você passou." if passou else "Não foi dessa vez..."
    cor = (0, 200, 0) if passou else (200, 0, 0)
    t0 = time.time()
    while time.time() - t0 < 2.0:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        surface.fill((0, 0, 0))
        txt = font.render(msg, True, cor)
        surface.blit(txt, ((LARGURA-txt.get_width())//2, ALTURA//2))
        pygame.display.flip()
        clock.tick(60)

    return passou

# --------------------- INITIAL POSITION --------------
def ajustar_posicao_inicial(jogador, obstaculos):
    while any(jogador.rect.colliderect(o.rect) for o in obstaculos):
        jogador.rect.y -= jogador.velocidade
        if jogador.rect.top <= 0:
            jogador.rect.top = 0
            jogador.rect.x += jogador.velocidade
            if jogador.rect.right >= LARGURA:
                jogador.rect.right = LARGURA
                break

# --------------------- MAIN GAME LOOP ----------------
def main():
    animations = load_animation_frames()
    jogador = Jogador(animations)
    grupo_jogador = pygame.sprite.Group(jogador)

    fases = [
        {
            "fundo": pygame.image.load("portaria.png").convert(),
            "obstaculos": [Obstaculo(300, 200, 200, 50)],
            "placas": [Placa(600, 300, 40, 40, "Bem-vindo à portaria!")],
            "itens":  [Item(400, 500, "Chave")],
            "area_transicao": pygame.Rect(0, 0, LARGURA, 5),
            "transicao_direcao": "top"
        },
        {
            "fundo": pygame.image.load("bolajardim.png").convert(),
            "obstaculos": [Obstaculo(100, 100, 400, 50)],
            "placas": [Placa(500, 600, 40, 40, "Aqui é o jardim central.")],
            "itens":  [],
            "area_transicao": pygame.Rect(0, ALTURA-5, LARGURA, 5),
            "transicao_direcao": "bottom"
        }
    ]
    fase_atual = 0
    ajustar_posicao_inicial(jogador, fases[0]["obstaculos"])

    lendo_placa  = False
    texto_placa  = ""
    placa_prox   = None
    quiz_pending = False
    evento_texto = ""
    evento_timer = 0

    transition_cd = 1.0
    last_transition = 0

    rodando = True
    while rodando:
        clock.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e and placa_prox:
                    lendo_placa = True; texto_placa = placa_prox.texto
                if evento.key == pygame.K_RETURN and lendo_placa:
                    lendo_placa = False
                if evento.key == pygame.K_q:   # <-- test trigger for quiz
                    quiz_pending = True

        fase = fases[fase_atual]
        grupo_obstaculos = pygame.sprite.Group(*fase["obstaculos"])
        grupo_placas     = pygame.sprite.Group(*fase["placas"])
        grupo_itens      = pygame.sprite.Group(*fase["itens"])

        teclas = pygame.key.get_pressed()
        if not lendo_placa and not quiz_pending:
            jogador.update(teclas, fase["obstaculos"])

        # ------------ Item collection ------------
        item_colidido = pygame.sprite.spritecollideany(jogador, grupo_itens)
        if item_colidido:
            jogador.coletar_item(item_colidido)
            grupo_itens.remove(item_colidido)

        # ------------ Stage transition -----------
        agora = time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and agora - last_transition > transition_cd:
            last_transition = agora
            x0, y0 = jogador.rect.center
            dir0   = fase["transicao_direcao"]
            fase_atual = (fase_atual + 1) % len(fases)
            nova = fases[fase_atual]
            if dir0 == "top":
                jogador.rect.midtop    = (x0, ALTURA - jogador.rect.height)
            elif dir0 == "bottom":
                jogador.rect.midbottom = (x0, 0)
            elif dir0 == "left":
                jogador.rect.midleft   = (LARGURA - jogador.rect.width, y0)
            elif dir0 == "right":
                jogador.rect.midright  = (0, y0)
            ajustar_posicao_inicial(jogador, nova["obstaculos"])

        # ------------ Quiz launch ---------------
        if quiz_pending:
            result = run_quiz(tela, fonte)
            evento_texto = "Evento A: Sucesso!" if result else "Evento B: Falha!"
            evento_timer = time.time()
            quiz_pending = False

        # ------------ DRAW ------------
        tela.blit(fase["fundo"], (0, 0))
        grupo_obstaculos.draw(tela)
        grupo_itens.draw(tela)
        grupo_placas.draw(tela)
        grupo_jogador.draw(tela)
        pygame.draw.rect(tela, (0, 255, 0), fase["area_transicao"], 2)

        # placa hint
        placa_prox = None
        for p in grupo_placas:
            if jogador.rect.colliderect(p.rect.inflate(40, 40)):
                placa_prox = p; break
        if placa_prox and not lendo_placa:
            hint = fonte.render("Pressione E para ler a placa", True, PRETO)
            tela.blit(hint, (jogador.rect.x - 40, jogador.rect.y - 30))

        # leitura da placa
        if lendo_placa:
            caixa = pygame.Rect(100, 600, 1000, 150)
            pygame.draw.rect(tela, BRANCO, caixa)
            pygame.draw.rect(tela, PRETO, caixa, 3)
            for i, linha in enumerate(texto_placa.split("\\n")):
                render = fonte.render(linha, True, PRETO)
                tela.blit(render, (120, 620 + i*30))

        # inventário HUD
        desenhar_inventario_top_right(tela, jogador.inventario)

        # resultado de evento pós‑quiz
        if evento_texto and time.time() - evento_timer < 2:
            txt = fonte.render(evento_texto, True, PRETO)
            tela.blit(txt, ((LARGURA - txt.get_width())//2, 50))
        elif time.time() - evento_timer >= 2:
            evento_texto = ""

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
