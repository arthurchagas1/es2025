import pygame, sys, os, time, random
from typing import List

pygame.init()
clock = pygame.time.Clock()

# ───────────────── CONSTANTES ─────────────────
LARGURA, ALTURA = 1200, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D – itens + quiz")

# ─── no topo do arquivo, logo após definir LARGURA/ALTURA ───
# função helper para carregar qualquer “nome.png” e seu “nome_mask.png”
def load_collision_mask_from(bg_filename, tol=(50,50,50)):
    # troca “.png” por “_mask.png”
    mask_filename = bg_filename.replace(".png", "_mask.png")
    raw = pygame.image.load(mask_filename).convert()
    scaled = pygame.transform.scale(raw, (LARGURA, ALTURA))
    return pygame.mask.from_threshold(scaled, (255,0,0), tol)

# máscara “vazia” para fallback (caso alguma fase não tenha mask)
default_mask = pygame.mask.Mask((LARGURA, ALTURA), fill=False)


BRANCO, CINZA   = (255,255,255), (100,100,100)
PRETO, VERDE    = (0,0,0), (0,255,0)
AZUL_CLARO      = (150,200,255)

# ────── FONTE PIXEL ──────
PIXEL_FONT = "fonts/PressStart2P-Regular.ttf"   # ajuste se necessário
try:
    fonte_dialog = pygame.font.Font(PIXEL_FONT, 30)
except FileNotFoundError:
    print("⚠️  Fonte PressStart2P não encontrada – usando sistema.")
    fonte_dialog = pygame.font.Font(None, 30)

fonte_hud = pygame.font.SysFont("Arial", 20)    # apenas HUD (inventário, ESC)

WOOD_IMG  = pygame.image.load("wood.png").convert()
ICON_OK   = pygame.transform.scale(pygame.image.load("ok.png").convert_alpha(),   (40,40))
ICON_FAIL = pygame.transform.scale(pygame.image.load("fail.png").convert_alpha(), (40,40))

# ───────── COLISÃO PIXEL-A-PIXEL: PORTARIA ─────────
raw_portaria_mask   = pygame.image.load("portaria_mask.png").convert()
# máscara “vazia” (nunca colide)
default_mask = pygame.mask.Mask((LARGURA, ALTURA), fill=False)

portaria_mask_surf  = pygame.transform.scale(raw_portaria_mask, (LARGURA, ALTURA))
# tol = (50,50,50) → considera qualquer tom 'quase-vermelho'
portaria_collision_mask = pygame.mask.from_threshold(
    portaria_mask_surf,
    (255,0,0),
    (50,50,50)
)
PLACA_IMG = pygame.image.load("sign.png").convert_alpha()


# ────────── ASSET HELPERS ──────────
def load_animation_frames(folder="animacoes", scale=0.15):
    frames=[]
    for i in range(16):
        img = pygame.image.load(os.path.join(folder,f"frame_{i}.png")).convert_alpha()
        w,h = img.get_size()
        frames.append(pygame.transform.scale(img,(int(w*scale),int(h*scale))))
    return {
        "down":  frames[0:4],
        "left":  frames[8:12],
        "right": frames[12:16],
        "up":    frames[4:8]
    }

def load_item_image(nome,size=(40,40)):
    path=os.path.join("itens",f"{nome}.png")
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(),size)
    surf=pygame.Surface(size,pygame.SRCALPHA); surf.fill((255,255,0))
    ch=fonte_dialog.render(nome[0].upper(),True,PRETO)
    surf.blit(ch,ch.get_rect(center=(size[0]//2,size[1]//2)))
    return surf

def load_npc_sprite(filename,scale=0.25,folder="animacoes2"):
    img=pygame.image.load(os.path.join(folder,filename)).convert_alpha()
    w,h=img.get_size()
    return pygame.transform.scale(img,(int(w*scale),int(h*scale)))

def load_bg(path:str):
    """Carrega o PNG/JPG e garante que ocupe toda a janela."""
    return pygame.transform.scale(
        pygame.image.load(path).convert(), 
        (LARGURA, ALTURA)
    )

def desenhar_barra_conhecimento(surf,valor,max_val=100):
    w,h=250,18
    bx=LARGURA-w-20; by=20
    pygame.draw.rect(surf,PRETO,(bx-2,by-2,w+4,h+4))
    pygame.draw.rect(surf,BRANCO,(bx,by,w,h))
    pct=valor/max_val
    pygame.draw.rect(surf,VERDE,(bx+2,by+2,int((w-4)*pct),h-4))
    surf.blit(fonte_hud.render(f"Conhecimento: {valor}/{max_val}",True,BRANCO),(bx,by+h+4))


# ───────────── SPRITES ─────────────
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self,x,y,w,h):
        super().__init__()
        self.image=pygame.Surface((w,h))
        self.image.fill(CINZA)
        self.rect=self.image.get_rect(topleft=(x,y))

class Placa(pygame.sprite.Sprite):
    def __init__(self, x, y, texto):
        super().__init__()
        self.image = pygame.transform.scale(PLACA_IMG, (64, 64))  # Adjust size if needed
        self.rect = self.image.get_rect(center=(x, y))
        self.texto = texto


class Item(pygame.sprite.Sprite):
    def __init__(self,x,y,nome):
        super().__init__()
        self.nome=nome
        self.image=load_item_image(nome)
        self.rect=self.image.get_rect(topleft=(x,y))

class Jogador(pygame.sprite.Sprite):
    def __init__(self, anim):
        super().__init__()
        self.anim         = anim
        self.dir          = "down"
        self.idx          = 0
        self.speed        = 5
        self.image        = anim["down"][0]
        self.rect         = self.image.get_rect(center=(LARGURA//2, ALTURA//2))
        # inventário: lista de tuples (nome, Surface)
        self.inv: List[tuple[str, pygame.Surface]] = []
        self.conhecimento = 0

    def coletar(self, item):
        """Adiciona item ao inventário, se ainda não estiver lá."""
        nomes = [n for n, _ in self.inv]
        if item.nome not in nomes:
            self.inv.append((item.nome, item.image))
            # opcional: ganha conhecimento por item
            self.conhecimento = min(self.conhecimento + 5, 100)

    def remover(self, nome: str):
        """Remove do inventário o item com esse nome."""
        self.inv = [(n, ic) for n, ic in self.inv if n != nome]

    def update(self, keys, obstaculos: List[Obstaculo], collision_mask: pygame.Mask):
        old_rect = self.rect.copy()
        moving   = False

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed; self.dir = "left";  moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed; self.dir = "right"; moving = True
        elif keys[pygame.K_UP]:
            self.rect.y -= self.speed; self.dir = "up";    moving = True
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.speed; self.dir = "down";  moving = True

        # colisão retangular com obstaculos
        for o in obstaculos:
            if self.rect.colliderect(o.rect):
                self.rect = old_rect
                break

        # mantém dentro da janela
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        # animação
        seq = self.anim[self.dir]
        if moving:
            self.idx = (self.idx + 0.15) % len(seq)
        else:
            self.idx = 0
        self.image = seq[int(self.idx)]

        # colisão pixel-a-pixel com a mask da fase
        self.mask = pygame.mask.from_surface(self.image)
        if collision_mask.overlap(self.mask, (self.rect.x, self.rect.y)):
            self.rect = old_rect



class NPC(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        super().__init__()
        self.image=image
        self.rect=image.get_rect(center=(x,y))
        self.falas:list[str]=[]
        self.idx=0
        self.ativo=False
        # Propriedade para identificar NPCs especiais
        self.tipo = None
    def iniciar_dialogo(self, falas:list[str]):
        self.falas=falas
        self.idx=0
        self.ativo=True
    def avancar_dialogo(self):
        self.idx+=1
        if self.idx>=len(self.falas):
            self.ativo=False


import math
# … tudo o mais igual …

# ───────── HUD INVENTÁRIO BONITINHO ─────────
INV_FONT_SIZE = 10
inv_font = pygame.font.Font("PressStart2P.ttf", INV_FONT_SIZE)

def render_text_with_border(text: str, fg: tuple, border: tuple, font: pygame.font.Font, border_size=1):
    """Renderiza texto com borda."""
    base = font.render(text, True, fg)
    w, h = base.get_width() + 2*border_size, base.get_height() + 2*border_size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in (-border_size, 0, border_size):
        for dy in (-border_size, 0, border_size):
            if dx or dy:
                surf.blit(font.render(text, True, border), (dx+border_size, dy+border_size))
    surf.blit(base, (border_size, border_size))
    return surf

def desenhar_inventario(surf, inv, y0):
    slot_size   = 48
    padding     = 16
    total_slots = 5

    panel_w = total_slots * slot_size + (total_slots + 1) * padding
    panel_h = slot_size + inv_font.get_height() + 3 + 2 * padding
    x0 = (LARGURA - panel_w) // 2

    painel = pygame.transform.scale(WOOD_IMG, (panel_w, panel_h))
    surf.blit(painel, (x0, y0))

    for i in range(total_slots):
        x = x0 + padding + i * (slot_size + padding)
        y = y0 + padding
        slot_rect = pygame.Rect(x, y, slot_size, slot_size)
        pygame.draw.rect(surf, PRETO, slot_rect, 2)

        if i < len(inv):
            nome, icon = inv[i]
            ic = pygame.transform.scale(icon, (slot_size - 8, slot_size - 8))
            surf.blit(ic, (x + 4, y + 4))
            txt = render_text_with_border(nome, BRANCO, PRETO, inv_font, border_size=1)
            tx = x + (slot_size - txt.get_width()) // 2
            ty = y + slot_size + 4
            surf.blit(txt, (tx, ty))



# ───────── QUIZ ─────────
class QuizQuestion:
    def __init__(self,q,opts,ans):
        self.q=q
        self.opts=opts
        self.ans=ans

QUESTOES=[
    QuizQuestion("Quantos cursos são ofertados no ICEx?",["3","10","15","20"],2),
    QuizQuestion("Quantos departamentos diferentes existem no ICEx?",["2","5","7","10"],1),
    QuizQuestion("Qual o cachorro que mais fica perambulando pelo prédio do ICEx?",["Banzé","Pretinha","Dexter","Jabuticaba"],2),
    QuizQuestion("Quem é o diretor do ICEx atualmente?",["Virgilio Almeida", "Reginaldo Santos", "Raquel Prates", "Francisco Dutenhefner"],3),
    QuizQuestion("Qual a melhor matéria ofertada no ICEx?",["ED","GAAL", "Cálculo I", "Engenharia de Software"],3)
]

def run_quiz(surface) -> tuple[int, bool]:
    perguntas = random.sample(QUESTOES, 5)
    acertos = 0
    for q in perguntas:
        sel, done = 0, False
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and not done:
                    if e.key in (pygame.K_UP, pygame.K_w):
                        sel = (sel - 1) % len(q.opts)
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        sel = (sel + 1) % len(q.opts)
                    elif e.key == pygame.K_RETURN:
                        done = True
                        if sel == q.ans:
                            acertos += 1
                        time.sleep(0.4)

            surface.fill((30, 30, 90))
            surface.blit(fonte_dialog.render(q.q, True, BRANCO), (60, 80))
            for i, opt in enumerate(q.opts):
                y = 200 + i * 60
                if i == sel:
                    pygame.draw.rect(surface, AZUL_CLARO, (50, y - 5, 700, 40))
                surface.blit(fonte_dialog.render(opt, True, BRANCO), (60, y))
            pygame.display.flip()
            clock.tick(60)
            if done:
                break

    passou = acertos >= 3
    return acertos, passou


# ...existing code...

# ─── ADDED: função para interação com Dexter ───
def run_dexter_interacao(surface):
    """
    Exibe duas opções: [Fazer carinho] ou [Não fazer].
    Retorna True se o jogador fizer carinho.
    """
    opcoes = ["Fazer carinho", "Ignorá-lo"]
    sel = 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(opcoes)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(opcoes)
                elif e.key == pygame.K_RETURN:
                    # Retorna True se escolheu "Fazer carinho"
                    return (sel == 0)
        surface.fill((30, 80, 30))
        surf_txt = fonte_dialog.render("O que fazer com Dexter?", True, BRANCO)
        surface.blit(surf_txt, (50, 50))
        for i, opt in enumerate(opcoes):
            y=150+i*60
            if i==sel:
                pygame.draw.rect(surface,AZUL_CLARO,(40,y-5,800,40))
            surface.blit(fonte_dialog.render(opt,True,BRANCO),(50,y))
        pygame.display.flip()
        clock.tick(60)

# ─── POSIÇÃO INICIAL ───
def ajustar_posicao_inicial(j,obs):
    while any(j.rect.colliderect(o.rect) for o in obs):
        j.rect.y-=j.speed
        if j.rect.top<=0:
            j.rect.top=0
            j.rect.x+=j.speed
            if j.rect.right>=LARGURA:
                j.rect.right=LARGURA
                break

def main():
    inv_visible   = False
    inv_speed     = 600
    SLOT_SIZE     = 48
    PADDING       = 16
    TOTAL_SLOTS   = 5
    panel_w = TOTAL_SLOTS * SLOT_SIZE + (TOTAL_SLOTS + 1) * PADDING
    panel_h = SLOT_SIZE + inv_font.get_height() + 3 + 2 * PADDING
    inv_visible_y = ALTURA - panel_h - 10
    inv_hidden_y  = ALTURA + 10
    inv_current_y = inv_hidden_y

    # ── CONFIGURAÇÕES INICIAIS ──
    anim        = load_animation_frames()
    jogador     = Jogador(anim)
    grupo_jog   = pygame.sprite.Group(jogador)
    jogador.rect.midbottom = (LARGURA // 2, ALTURA - 50)

    natalie_sprite = load_npc_sprite("frame_13.png", scale=1.25)
    natalie = NPC(9 * LARGURA / 10, 1 * ALTURA / 8, natalie_sprite)

    dexter_sprite = load_npc_sprite("frame_3.png", scale=0.035, folder="animacoes_dexter")
    dexter = NPC(400, 500, dexter_sprite)
    dexter.tipo = "dexter"
    dexter_interacted = False

    single_sprite = load_npc_sprite("frame_13.png", folder="animacoes3", scale=1.4)
    padding = 10
    w, h = single_sprite.get_size()
    combined_sprite = pygame.Surface((w, h * 2 + padding), pygame.SRCALPHA)
    combined_sprite.blit(single_sprite, (0, 0))
    combined_sprite.blit(single_sprite, (0, h + padding))
    porteiro = NPC(330, 530, combined_sprite)

    # Professor
    professor_sprite = load_npc_sprite("frame_12.png", scale=1.3, folder="animacoes_meira")
    professor = NPC(LARGURA - 120, ALTURA - 200, professor_sprite)
    professor.tipo = "professor"

    quest_target = pygame.Rect(0, ALTURA // 2 - 200, 210, 300)

    fases = [
        # … (mesma lista de fases que você já tem, com professor na fase 5) …
        # (copiei sem alterações)
        {
            "fundo": load_bg("portaria.png"),
            "collision_mask": load_collision_mask_from("portaria.png"),
            "obstaculos": [],
            "placas": [Placa(LARGURA // 2, ALTURA / 3,
                     "Bem‑vindo ao ICEx!\nVocê está na portaria principal!, do outro lado da rua, temos o prédio da engenharia!\nAqui dentro você vai encontrar salas de aula, laboratórios e nossos lindos jardins!")],
            "itens": [],
            "npcs": [porteiro],
            "transicoes": [{"rect": pygame.Rect(0, 0, LARGURA, 5), "dest": 1, "spawn_side": "bottom"}]
        },
        {
            "fundo": load_bg("bolajardim.png"),
            "collision_mask": load_collision_mask_from("bolajardim.png"),
            "obstaculos": [],
            "placas": [Placa(LARGURA // 2, ALTURA // 2,
                     "Este é o famoso jardim da bola do ICEx, aqui você pode descansar,\nencontrar amigos e aproveitar a fauna a a flora nativa!")],
            "itens": [],
            "quest_target": quest_target,
            "npcs": [],
            "transicoes": [
                {"rect": pygame.Rect(0, ALTURA - 5, LARGURA, 5), "dest": 0, "spawn_side": "top"},
                {"rect": pygame.Rect(0, 0, LARGURA, 5), "dest": 2, "spawn_side": "bottom"}
            ]
        },
        {
            "fundo": load_bg("salas1.png"),
            "collision_mask": load_collision_mask_from("salas1.png"),
            "obstaculos": [],
            "placas": [Placa(LARGURA // 2, ALTURA // 2-50,
                     "Aqui são as salas de aula do ICEx,\nonde você vai passar a maior parte do seu tempo!\nQuem é aquela mulher ali? Melhor ir lá descobrir!")],
            "itens": [],
            "npcs": [natalie],
            "transicoes": [
                {"rect": pygame.Rect(0, ALTURA - 5, LARGURA, 5), "dest": 1, "spawn_side": "top"},
                {"rect": pygame.Rect(LARGURA - 5, 0, 5, ALTURA), "dest": 3, "spawn_side": "left"}
            ]
        },
        {
            "fundo": load_bg("salas2.png"),
            "collision_mask": load_collision_mask_from("salas2.png"),
            "obstaculos": [],
            "placas": [Placa(LARGURA // 2, ALTURA // 2-50,
                     "Mais salas! Acima, também temos outra portaria, que dá acesso à praça de serviços\ne a outros prédios, como o ICB! (A cantina de lá é muito boa! Tem churros e salgado!)")],
            "itens": [],
            "npcs": [],
            "transicoes": [
                {"rect": pygame.Rect(0, 0, 5, ALTURA), "dest": 2, "spawn_side": "right"},
                {"rect": pygame.Rect(0, ALTURA - 5, LARGURA, 5), "dest": 4, "spawn_side": "top"}
            ]
        },
        {
            "fundo": load_bg("jardim2.png"),
            "collision_mask": load_collision_mask_from("jardim2.png"),
            "obstaculos": [],
            "placas": [Placa(LARGURA // 2, ALTURA // 2,
                     "Mais um lugar tranquilo para descansar e divagar sobre o sentido da vida.\nComo disse Sócrates: 'Uma vida não examinada não vale a pena ser vivida…'\nO que estou dizendo? A prova de ED é em alguns minutos! Melhor ir logo!")],
            "itens": [],
            "npcs": [dexter],
            "transicoes": [
                {"rect": pygame.Rect(0, 0, LARGURA, 5), "dest": 3, "spawn_side": "bottom"},
                {"rect": pygame.Rect(0, ALTURA - 5, LARGURA, 5), "dest": 5, "spawn_side": "top"}
            ]
        },
        {
            "fundo": load_bg("corredorfinal.png"),
            "collision_mask": load_collision_mask_from("corredorfinal.png"),
            "obstaculos": [],
            "placas": [Placa(LARGURA // 2, ALTURA // 2, "Corredor final.\nBoa sorte na prova!")],
            "itens": [],
            "npcs": [professor],
            "transicoes": [
                {"rect": pygame.Rect(0, 0, LARGURA, 5), "dest": 4, "spawn_side": "bottom"}
            ]
        }
    ]

    fase_idx = 0
    ajustar_posicao_inicial(jogador, fases[0]["obstaculos"])

    # ── VARIÁVEIS DE ESTADO ──
    lendo_placa = False
    texto_placa = ""
    placa_prox = npc_prox = None
    quiz_pending = False            # só do porteiro
    evento_txt = ""
    evento_timer = 0
    item_msg = ""
    item_timer = 0
    quest_state = "not_started"
    transition_cd, last_transition = 1.0, 0
    restart_to_menu = False
    end_screen = None               # "pass" | "fail" | None

    rodando = True
    while rodando:
        dt = clock.tick(60) / 1000.0

        # Inventário deslizando
        target_y = inv_visible_y if inv_visible else inv_hidden_y
        if inv_current_y < target_y:
            inv_current_y = min(inv_current_y + inv_speed * dt, target_y)
        elif inv_current_y > target_y:
            inv_current_y = max(inv_current_y - inv_speed * dt, target_y)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    choice = __import__("main").tela_config(tela.copy())
                    if choice == "menu":
                        restart_to_menu = True; rodando = False

                elif ev.key == pygame.K_e and placa_prox and not npc_prox:
                    lendo_placa, texto_placa = True, placa_prox.texto

                elif ev.key == pygame.K_RETURN and lendo_placa:
                    lendo_placa = False

                elif ev.key == pygame.K_i:
                    inv_visible = not inv_visible

                # ── Interações com NPCs ──
                elif ev.key == pygame.K_e and npc_prox and not npc_prox.ativo and not lendo_placa:
                    if npc_prox.tipo == "dexter" and not dexter_interacted:
                        fez_carinho = run_dexter_interacao(tela)
                        if fez_carinho:
                            jogador.conhecimento = min(jogador.conhecimento + 25, 100)
                            evento_txt = "+25 conhecimento! Dexter está feliz!"
                            npc_prox.iniciar_dialogo([
                                "Dexter ficou feliz com o carinho!",
                                "Ele te deu um resumo de ED (+25 conhecimento)."
                            ])
                            jogador.coletar(Item(0, 0, "Resumo de ED"))
                        else:
                            evento_txt = "Dexter parece triste…"
                            npc_prox.iniciar_dialogo(["Dexter ficou triste por não receber carinho."])
                        evento_timer = time.time(); dexter_interacted = True

                    elif npc_prox == porteiro:
                        porteiro.iniciar_dialogo([
                            "P: Bom dia, estudante!",
                            "Bom dia Porteiro! Estou indo para a prova.",
                            "Eu esqueci minha carteirinha, posso entrar?",
                            "P: Não pode entrar sem carteirinha!",
                            "P: Como vou saber se você é estudante?",
                            "Não se preocupe, eu sou estudante sim! Eu posso provar!",
                            "P: Então prove! Responda a esse quiz sobre o ICEx e a UFMG.",
                            "P: Só um verdadeiro estudante consegue passar!",
                            "Estou pronto!"
                        ])

                    elif npc_prox == natalie:
                        if quest_state == "not_started":
                            falas = [
                                "Natalie! Que bom que você está aqui, tenho uma prova agora,\npreciso muito de uma caneta emprestada…",
                                "N: Oi meu amor, eu tenho uma caneta da boa bem aqui, mas antes,\npreciso que você me ajude: tire uma foto na bola do ICEx!",
                                "N: Depois, volte aqui e me mostre!",
                                "Ok, vou tirar a foto e já volto!",
                                "N: Ah, e não esquece de pegar a câmera na minha mochila!"
                            ]
                            natalie.iniciar_dialogo(falas)

                        elif quest_state == "in_progress":
                            natalie.iniciar_dialogo(["Você ainda não tirou a foto!"])

                        elif quest_state == "photo_taken":
                            natalie.iniciar_dialogo([
                                "Uau, ficou ótima!",
                                "Aqui está sua caneta",
                                "Boa prova!"
                            ])

                        else:
                            natalie.iniciar_dialogo(["Boa sorte na prova!"])

                    elif npc_prox == professor:
                        has_pen = any(n == "Caneta" for n, _ in jogador.inv)
                        if jogador.conhecimento >= 40 and has_pen:
                            professor.iniciar_dialogo([
                                "Professor: Chegou a tempo.",
                                "Professor: Se já estudou bastante, vamos ver o resultado…"
                            ])
                        else:
                            professor.iniciar_dialogo([
                                "Professor: Volte com pelo menos 40 de conhecimento",
                                "e não esqueça da caneta!"
                            ])

                elif ev.key == pygame.K_RETURN and npc_prox and npc_prox.ativo:
                    npc_prox.avancar_dialogo()

                    # Depois que o porteiro termina -> quiz
                    if npc_prox == porteiro and not npc_prox.ativo:
                        quiz_pending = True

                    # Depois que Natalie termina
                    if npc_prox == natalie and not npc_prox.ativo:
                        if quest_state == "not_started":
                            jogador.coletar(Item(0, 0, "Camera"))
                            item_msg = "Câmera adicionada!"
                            item_timer = time.time(); quest_state = "in_progress"
                        elif quest_state == "photo_taken":
                            jogador.remover("Camera"); jogador.coletar(Item(0, 0, "Caneta"))
                            item_msg = "Caneta adicionada!"
                            item_timer = time.time(); quest_state = "done"

                    # Depois que Professor termina -> tela final
                    if npc_prox == professor and not npc_prox.ativo:
                        has_pen = any(n == "Caneta" for n, _ in jogador.inv)
                        if jogador.conhecimento >= 40 and has_pen:
                            end_screen = "pass" if jogador.conhecimento >= 60 else "fail"
                            evento_timer = time.time()

        # Bloqueia movimento quando a tela final estiver ativa
        if end_screen:
            tela.fill((0, 0, 0))
            big_font = pygame.font.Font("PressStart2P.ttf", 48)
            msg = "PARABÉNS, VOCÊ PASSOU!" if end_screen == "pass" else "VOCÊ BOMBOU EM ED!"
            
            txt = big_font.render(msg, True, (255, 255, 0) if end_screen == "pass" else (255, 0, 0))
            tela.blit(txt, txt.get_rect(center=(LARGURA // 2, ALTURA // 2)))
            pygame.display.flip()

            # Depois de 5 s volta ao menu
            if time.time() - evento_timer > 5:
                restart_to_menu = True; rodando = False
            continue   # pula o restante do loop

        # ── ATUALIZAÇÕES NORMAIS ──
        fase = fases[fase_idx]
        grupo_obs = pygame.sprite.Group(*fase["obstaculos"])
        grupo_pla = pygame.sprite.Group(*fase["placas"])
        grupo_itm = pygame.sprite.Group(*fase["itens"])
        grupo_npc = pygame.sprite.Group(*fase["npcs"])

        keys = pygame.key.get_pressed()
        if not (lendo_placa or quiz_pending or (npc_prox and npc_prox.ativo)):
            mask = fase.get("collision_mask", default_mask)
            jogador.update(keys, fase["obstaculos"], mask)

        # Foto para Natalie
        dentro_area_foto = quest_state == "in_progress" and jogador.rect.colliderect(quest_target)
        if dentro_area_foto and keys[pygame.K_f]:
            quest_state = "photo_taken"
            evento_txt = "Foto tirada! Volte para Natalie."
            evento_timer = time.time()

        # Transições
        agora = time.time()
        for t in fase["transicoes"]:
            if jogador.rect.colliderect(t["rect"]) and agora - last_transition > transition_cd:
                last_transition = agora; fase_idx = t["dest"]
                next_fase = fases[fase_idx]
                cx, cy = jogador.rect.center; side = t["spawn_side"]
                if side == "top":
                    jogador.rect.midtop = (cx, 0)
                elif side == "bottom":
                    jogador.rect.midbottom = (cx, ALTURA)
                elif side == "left":
                    jogador.rect.midleft = (0, cy)
                else:
                    jogador.rect.midright = (LARGURA, cy)
                ajustar_posicao_inicial(jogador, next_fase["obstaculos"])
                break

        # Quiz do porteiro
        if quiz_pending:
            acertos, _ = run_quiz(tela)
            ganho = acertos * 10
            jogador.conhecimento = min(jogador.conhecimento + ganho, 100)
            evento_txt = (f"{acertos}/5 corretas! +{ganho} conhecimento!"
                          if acertos >= 3 else f"{acertos}/5 corretas. Tente de novo!")
            evento_timer = time.time(); quiz_pending = False

        # ── DESENHO DA FASE ──
        tela.blit(fase["fundo"], (0, 0))
        grupo_obs.draw(tela); grupo_itm.draw(tela)
        grupo_pla.draw(tela); grupo_npc.draw(tela); grupo_jog.draw(tela)

        #if quest_state == "in_progress":
        #    pygame.draw.rect(tela, (255, 255, 0), quest_target, 2)

        # Proximidades
        placa_prox = next((p for p in grupo_pla if jogador.rect.colliderect(p.rect.inflate(40, 40))), None)
        npc_prox = None
        for npc in grupo_npc:
            if npc == porteiro:
                zone = pygame.Rect(npc.rect.right + 100, npc.rect.top, 60, npc.rect.height)
                if jogador.rect.colliderect(zone): npc_prox = npc; break
            else:
                if jogador.rect.colliderect(npc.rect.inflate(50, 50)): npc_prox = npc; break

        # Dicas
        if (placa_prox or npc_prox) and not lendo_placa and not (npc_prox and npc_prox.ativo):
            tip = fonte_dialog.render("Pressione E para interagir", True, PRETO)
            bg = pygame.Rect(0, 0, tip.get_width() + 20, tip.get_height() + 10)
            bg.midbottom = (jogador.rect.centerx, jogador.rect.y - 10)
            s = pygame.Surface(bg.size, pygame.SRCALPHA); s.fill((255, 255, 255, 200))
            tela.blit(s, bg.topleft); pygame.draw.rect(tela, PRETO, bg, 2)
            tela.blit(tip, (bg.x + 10, bg.y + 5))

        if dentro_area_foto:
            tip = fonte_dialog.render("Pressione F para tirar foto", True, PRETO)
            bg = pygame.Rect(0, 0, tip.get_width() + 20, tip.get_height() + 10)
            bg.midbottom = (jogador.rect.centerx, jogador.rect.y - 50)
            s = pygame.Surface(bg.size, pygame.SRCALPHA); s.fill((255, 255, 255, 200))
            tela.blit(s, bg.topleft); pygame.draw.rect(tela, PRETO, bg, 2)
            tela.blit(tip, (bg.x + 10, bg.y + 5))

        # Caixa de placas
        if lendo_placa:
            caixa = pygame.Rect(100, 600, 1000, 150)
            tela.blit(pygame.transform.scale(WOOD_IMG, caixa.size), caixa.topleft)
            pygame.draw.rect(tela, BRANCO, caixa, 3)
            for i, linha in enumerate(texto_placa.split("\n")):
                rend = render_text_with_border(linha, BRANCO, PRETO, fonte_dialog, 1.2)
                tela.blit(rend, (caixa.x + 20, caixa.y + 20 + i * 36))

        # Caixa de diálogo de NPC
        if npc_prox and npc_prox.ativo:
            caixa = pygame.Rect(80, 580, 1040, 160)
            tela.blit(pygame.transform.scale(WOOD_IMG, caixa.size), caixa.topleft)
            pygame.draw.rect(tela, BRANCO, caixa, 3)
            linha = npc_prox.falas[npc_prox.idx]
            for i, parte in enumerate(linha.split("\n")):
                rend = render_text_with_border(parte, BRANCO, PRETO, fonte_dialog, 1.2)
                tela.blit(rend, (caixa.x + 20, caixa.y + 50 + i * 36))

        # HUD
        desenhar_inventario(tela, jogador.inv, inv_current_y)
        desenhar_barra_conhecimento(tela, jogador.conhecimento)

        # Mensagens de evento / item
        if evento_txt and time.time() - evento_timer < 3:
            msg = fonte_dialog.render(evento_txt, True, PRETO)
            bg = pygame.Rect(0, 0, msg.get_width() + 40, msg.get_height() + 20)
            bg.center = (LARGURA // 2, 40)
            s = pygame.Surface(bg.size, pygame.SRCALPHA); s.fill((255, 255, 255, 230))
            tela.blit(s, bg.topleft); pygame.draw.rect(tela, PRETO, bg, 2)
            tela.blit(msg, (bg.x + 20, bg.y + 10))
        elif time.time() - evento_timer >= 3:
            evento_txt = ""

        if item_msg and time.time() - item_timer < 3:
            msg = fonte_dialog.render(item_msg, True, PRETO)
            bg = pygame.Rect(0, 0, msg.get_width() + 40, msg.get_height() + 20)
            bg.center = (LARGURA // 2, 40)
            s = pygame.Surface(bg.size, pygame.SRCALPHA); s.fill((255, 255, 255, 230))
            tela.blit(s, bg.topleft); pygame.draw.rect(tela, PRETO, bg, 2)
            tela.blit(msg, (bg.x + 20, bg.y + 10))
        elif time.time() - item_timer >= 3:
            item_msg = ""

        esc_tip = render_text_with_border("Esc – Pausa/Config.", BRANCO, PRETO,
                                          pygame.font.Font("PressStart2P.ttf", 16), 1)
        tela.blit(esc_tip, (10, 10))

        pygame.display.flip()

    return "menu" if restart_to_menu else None
