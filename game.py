import pygame, sys, os, time, random
from typing import List

pygame.init()
clock = pygame.time.Clock()

# ───────────────── CONSTANTES ─────────────────
LARGURA, ALTURA = 1200, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D – itens + quiz")

BRANCO = (255, 255, 255)
CINZA  = (100, 100, 100)
PRETO  = (  0,   0,   0)
VERDE  = (  0, 255,   0)
AZUL_CLARO = (150, 200, 255)

fonte      = pygame.font.SysFont("Arial", 24)
fonte_hud  = pygame.font.SysFont("Arial", 20)   # dica Esc

# ──────────────── ASSET HELPERS ───────────────
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
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    # fallback
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((255, 255, 0))
    letter = fonte.render(nome[0].upper(), True, PRETO)
    surf.blit(letter, letter.get_rect(center=(size[0]//2, size[1]//2)))
    return surf

def load_icon(path, color):
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (40,40))
    surf = pygame.Surface((40,40), pygame.SRCALPHA)
    surf.fill(color); return surf

ICON_OK   = load_icon("ok.png",   (0,255,0))
ICON_FAIL = load_icon("fail.png", (255,0,0))

# ───────────────── SPRITE CLASSES ─────────────
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h):
        super().__init__()
        self.image = pygame.Surface((w,h)); self.image.fill(CINZA)
        self.rect  = self.image.get_rect(topleft=(x,y))

class Placa(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h,texto):
        super().__init__()
        self.image = pygame.Surface((w,h)); self.image.fill(VERDE)
        self.rect  = self.image.get_rect(topleft=(x,y))
        self.texto = texto

class Item(pygame.sprite.Sprite):
    def __init__(self, x,y,nome):
        super().__init__()
        self.nome  = nome
        self.image = load_item_image(nome)
        self.rect  = self.image.get_rect(topleft=(x,y))

class Jogador(pygame.sprite.Sprite):
    def __init__(self, anim):
        super().__init__()
        self.anim  = anim
        self.dir   = "down"
        self.idx   = 0
        self.speed = 5
        self.image = anim["down"][0]
        self.rect  = self.image.get_rect(center=(LARGURA//2, ALTURA//2))
        self.inv: List[tuple[str, pygame.Surface]] = []

    def coletar(self, item: Item):
        if item.nome not in [n for n,_ in self.inv]:
            self.inv.append((item.nome, item.image))

    def update(self, keys, obstaculos):
        old = self.rect.copy()
        moving=False
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed; self.dir="left"; moving=True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed; self.dir="right"; moving=True
        elif keys[pygame.K_UP]:
            self.rect.y -= self.speed; self.dir="up"; moving=True
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.speed; self.dir="down"; moving=True

        for o in obstaculos:
            if self.rect.colliderect(o.rect): self.rect=old; break
        self.rect.clamp_ip(pygame.Rect(0,0,LARGURA,ALTURA))

        self.idx = (self.idx+0.15) % len(self.anim[self.dir]) if moving else 0
        self.image = self.anim[self.dir][int(self.idx)]

# ─────────────── INVENTÁRIO HUD ───────────────
def desenhar_inventario(surface, inv):
    x=LARGURA-50
    for nome,icon in reversed(inv):
        surface.blit(icon,(x,10))
        surface.blit(fonte.render(nome,True,PRETO),(x-110,15))
        x-=120

# ─────────────── QUIZ UTILITIES ───────────────
class QuizQuestion:
    def __init__(self, q, opts, ans):
        self.q=q; self.opts=opts; self.ans=ans

QUESTOES=[
    QuizQuestion("Quanto é 2 + 2?",["3","4","5","22"],1),
    QuizQuestion("Qual linguagem estamos usando?",["Java","C++","Python","Ruby"],2),
    QuizQuestion("Qual planeta é conhecido como o Planeta Vermelho?",["Terra","Vênus","Marte","Júpiter"],2),
    QuizQuestion("Quem pintou a Mona Lisa?",["Van Gogh","Da Vinci","Picasso","Michelangelo"],1),
    QuizQuestion("Em que continente fica o Brasil?",["África","Europa","Ásia","América do Sul"],3),
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
            # ── events ──
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

# ───────────── POSIÇÃO INICIAL ────────────────
def ajustar_posicao_inicial(j,obs):
    while any(j.rect.colliderect(o.rect) for o in obs):
        j.rect.y-=j.speed
        if j.rect.top<=0:
            j.rect.top=0; j.rect.x+=j.speed
            if j.rect.right>=LARGURA:
                j.rect.right=LARGURA; break

# ───────────────── MAIN LOOP ──────────────────
def main():
    animations = load_animation_frames()
    jogador = Jogador(animations)
    grupo_jogador = pygame.sprite.Group(jogador)

    fases=[
        {"fundo":pygame.image.load("portaria.png").convert(),
         "obstaculos":[Obstaculo(300,200,200,50)],
         "placas":[Placa(600,300,40,40,"Bem-vindo à portaria!")],
         "itens":[Item(400,500,"Chave")],
         "area_transicao":pygame.Rect(0,0,LARGURA,5),
         "transicao_direcao":"top"},
        {"fundo":pygame.image.load("bolajardim.png").convert(),
         "obstaculos":[Obstaculo(100,100,400,50)],
         "placas":[Placa(500,600,40,40,"Aqui é o jardim central.")],
         "itens":[],
         "area_transicao":pygame.Rect(0,ALTURA-5,LARGURA,5),
         "transicao_direcao":"bottom"}
    ]
    fase_idx=0
    ajustar_posicao_inicial(jogador,fases[0]["obstaculos"])

    lendo_placa=False; texto_placa=""
    placa_prox=None
    quiz_pending=False
    evento_txt=""; evento_timer=0
    transition_cd,last_transition=1.0,0

    restart_to_menu=False   # flag para voltar ao menu

    rodando=True
    while rodando:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit(); sys.exit()

            # pausa/config
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                snapshot=pygame.display.get_surface().copy()
                import sys, importlib
                main_mod=sys.modules.get("main") or importlib.import_module("main")
                choice=main_mod.tela_config(snapshot)
                if choice=="menu":   # jogador escolheu voltar ao menu
                    restart_to_menu=True
                    rodando=False
                    break

            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_e and placa_prox:
                    lendo_placa=True; texto_placa=placa_prox.texto
                if ev.key==pygame.K_RETURN and lendo_placa:
                    lendo_placa=False
                if ev.key==pygame.K_q:
                    quiz_pending=True

        if not rodando:
            break

        fase=fases[fase_idx]
        grupo_obs = pygame.sprite.Group(*fase["obstaculos"])
        grupo_pla = pygame.sprite.Group(*fase["placas"])
        grupo_itm = pygame.sprite.Group(*fase["itens"])

        keys=pygame.key.get_pressed()
        if not lendo_placa and not quiz_pending:
            jogador.update(keys, fase["obstaculos"])

        # coletar item
        item_hit=pygame.sprite.spritecollideany(jogador, grupo_itm)
        if item_hit:
            jogador.coletar(item_hit)
            grupo_itm.remove(item_hit)

        # transição de fase
        agora=time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and agora-last_transition>transition_cd:
            last_transition=agora
            x0,y0=jogador.rect.center
            dir0=fase["transicao_direcao"]
            fase_idx=(fase_idx+1)%len(fases)
            nova=fases[fase_idx]
            if dir0=="top":     jogador.rect.midtop    =(x0,ALTURA-jogador.rect.height)
            elif dir0=="bottom":jogador.rect.midbottom=(x0,0)
            elif dir0=="left":  jogador.rect.midleft   =(LARGURA-jogador.rect.width,y0)
            elif dir0=="right": jogador.rect.midright  =(0,y0)
            ajustar_posicao_inicial(jogador,nova["obstaculos"])

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

        placa_prox=next((p for p in grupo_pla if jogador.rect.colliderect(p.rect.inflate(40,40))),None)
        if placa_prox and not lendo_placa:
            tela.blit(fonte.render("Pressione E para ler a placa",True,PRETO),
                      (jogador.rect.x-40,jogador.rect.y-30))

        if lendo_placa:
            caixa=pygame.Rect(100,600,1000,150)
            pygame.draw.rect(tela,BRANCO,caixa); pygame.draw.rect(tela,PRETO,caixa,3)
            for i,linha in enumerate(texto_placa.split("\\n")):
                tela.blit(fonte.render(linha,True,PRETO),(120,620+i*30))

        desenhar_inventario(tela,jogador.inv)

        if evento_txt and time.time()-evento_timer<2:
            tela.blit(fonte.render(evento_txt,True,PRETO),
                      ((LARGURA-fonte.size(evento_txt)[0])//2,50))
        elif time.time()-evento_timer>=2:
            evento_txt=""

        tela.blit(fonte_hud.render("Esc – Pausa/Config.",True,(255,255,0)),(10,10))

        pygame.display.flip()

    if restart_to_menu:
        return "menu"         # sinaliza para main.py reiniciar
    return None               # jogo terminou normalmente

if __name__=="__main__":
    main()
