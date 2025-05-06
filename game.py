import pygame, sys, os, time, random
from typing import List



pygame.init()
clock = pygame.time.Clock()

# ───────────────── CONSTANTES ─────────────────
LARGURA, ALTURA = 1200, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D – itens + quiz")

BRANCO, CINZA   = (255,255,255), (100,100,100)
PRETO, VERDE    = (0,0,0), (0,255,0)
AZUL_CLARO      = (150,200,255)

# ────── FONTE PIXEL ──────
PIXEL_FONT = "fonts/PressStart2P-Regular.ttf"   # ajuste se necessário
try:
    fonte_dialog = pygame.font.Font(PIXEL_FONT, 40)
except FileNotFoundError:
    print("⚠️  Fonte PressStart2P não encontrada – usando sistema.")
    fonte_dialog = pygame.font.Font(None, 40)

fonte_hud = pygame.font.SysFont("Arial", 20)    # apenas HUD (inventário, ESC)

WOOD_IMG  = pygame.image.load("wood.png").convert()
ICON_OK   = pygame.transform.scale(pygame.image.load("ok.png").convert_alpha(),   (40,40))
ICON_FAIL = pygame.transform.scale(pygame.image.load("fail.png").convert_alpha(), (40,40))

# ────────── ASSET HELPERS ──────────
def load_animation_frames(folder="animacoes", scale=0.15):
    frames=[]
    for i in range(16):
        img = pygame.image.load(os.path.join(folder,f"frame_{i}.png")).convert_alpha()
        w,h = img.get_size()
        frames.append(pygame.transform.scale(img,(int(w*scale),int(h*scale))))
    return {"down":frames[0:4], "left":frames[8:12],
            "right":frames[12:16], "up":frames[4:8]}

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


# ───────────── SPRITES ─────────────
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self,x,y,w,h):
        super().__init__(); self.image=pygame.Surface((w,h)); self.image.fill(CINZA)
        self.rect=self.image.get_rect(topleft=(x,y))

class Placa(pygame.sprite.Sprite):
    def __init__(self,x,y,w,h,texto):
        super().__init__()
        self.image=pygame.Surface((w,h)); self.image.fill(VERDE)
        self.rect=self.image.get_rect(topleft=(x,y))
        self.texto=texto

class Item(pygame.sprite.Sprite):
    def __init__(self,x,y,nome):
        super().__init__()
        self.nome=nome; self.image=load_item_image(nome)
        self.rect=self.image.get_rect(topleft=(x,y))

class Jogador(pygame.sprite.Sprite):
    def __init__(self,anim):
        super().__init__()
        self.anim, self.dir, self.idx = anim,"down",0
        self.speed=5
        self.image=anim["down"][0]
        self.rect=self.image.get_rect(center=(LARGURA//2,ALTURA//2))
        self.inv:List[tuple[str,pygame.Surface]]=[]
    def coletar(self,item):
        if item.nome not in [n for n,_ in self.inv]:
            self.inv.append((item.nome,item.image))
    def remover(self, nome:str):
        self.inv = [(n, ic) for n, ic in self.inv if n != nome]

    def update(self,keys,obs):
        old=self.rect.copy(); moving=False
        if keys[pygame.K_LEFT]:  self.rect.x-=self.speed; self.dir="left";  moving=True
        elif keys[pygame.K_RIGHT]:self.rect.x+=self.speed; self.dir="right"; moving=True
        elif keys[pygame.K_UP]:  self.rect.y-=self.speed; self.dir="up";    moving=True
        elif keys[pygame.K_DOWN]:self.rect.y+=self.speed; self.dir="down";  moving=True
        for o in obs:
            if self.rect.colliderect(o.rect): self.rect=old; break
        self.rect.clamp_ip(pygame.Rect(0,0,LARGURA,ALTURA))
        self.idx=(self.idx+0.15)%len(self.anim[self.dir]) if moving else 0
        self.image=self.anim[self.dir][int(self.idx)]

class NPC(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        super().__init__(); self.image=image; self.rect=image.get_rect(center=(x,y))
        self.falas:list[str]=[]; self.idx=0; self.ativo=False
    def iniciar_dialogo(self, falas:list[str]):
        self.falas=falas; self.idx=0; self.ativo=True
    def avancar_dialogo(self):
        self.idx+=1
        if self.idx>=len(self.falas): self.ativo=False

import math
# … tudo o mais igual …

# ───────── HUD INVENTÁRIO BONITINHO ─────────
# Carregue a fonte de inventário lá no topo, junto com a de 16-bits:
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

def desenhar_inventario(surf, inv):
    """
    Desenha o inventário sempre com 5 slots,
    centralizado horizontalmente e posicionado na parte de baixo da tela,
    com espaçamento maior entre os itens.
    """
    slot_size   = 48
    padding     = 16   # mais espaço entre slots
    total_slots = 5

    # calcula tamanho do painel
    panel_w = total_slots * slot_size + (total_slots + 1) * padding
    panel_h = slot_size + inv_font.get_height() + 3 + 2 * padding

    # posição: meio-x e 10px acima da borda inferior
    x0 = (LARGURA - panel_w) // 2
    y0 = ALTURA - panel_h - 10

    # desenha o painel de madeira
    painel = pygame.transform.scale(WOOD_IMG, (panel_w, panel_h))
    surf.blit(painel, (x0, y0))

    for i in range(total_slots):
        # coord de cada slot
        x = x0 + padding + i * (slot_size + padding)
        y = y0 + padding

        # retângulo do slot
        slot_rect = pygame.Rect(x, y, slot_size, slot_size)
        pygame.draw.rect(surf, PRETO, slot_rect, 2)

        # se houver item nesse slot, desenha ícone e nome
        if i < len(inv):
            nome, icon = inv[i]
            # ícone centralizado dentro do slot
            ic = pygame.transform.scale(icon, (slot_size - 8, slot_size - 8))
            surf.blit(ic, (x + 4, y + 4))

            # nome abaixo do slot, com fonte PressStart2P e borda preta
            txt = render_text_with_border(nome, BRANCO, PRETO, inv_font, border_size=1)
            tx = x + (slot_size - txt.get_width()) // 2
            ty = y + slot_size + 4
            surf.blit(txt, (tx, ty))




# ───────── QUIZ ─────────
class QuizQuestion:
    def __init__(self,q,opts,ans): self.q=q; self.opts=opts; self.ans=ans
QUESTOES=[QuizQuestion("Quanto é 2 + 2?",["3","4","5","22"],1),
          QuizQuestion("Qual linguagem estamos usando?",["Java","C++","Python","Ruby"],2),
          QuizQuestion("Qual planeta é vermelho?",["Terra","Vênus","Marte","Júpiter"],2)]
def run_quiz(surface)->bool:
    perguntas=random.sample(QUESTOES,3); acertos=0
    for q in perguntas:
        sel,answered,icon,t0=0,False,None,0
        while True:
            for e in pygame.event.get():
                
                if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN and not answered:
                    if e.key in (pygame.K_UP,pygame.K_w): sel=(sel-1)%len(q.opts)
                    elif e.key in (pygame.K_DOWN,pygame.K_s): sel=(sel+1)%len(q.opts)
                    elif e.key==pygame.K_RETURN:
                        answered=True; correct=(sel==q.ans)
                        icon=ICON_OK if correct else ICON_FAIL
                        if correct: acertos+=1; t0=time.time()
            surface.fill((30,30,90))
            surface.blit(fonte_dialog.render(q.q,True,BRANCO),(60,80))
            for i,opt in enumerate(q.opts):
                y=200+i*60
                if i==sel: pygame.draw.rect(surface,AZUL_CLARO,(50,y-5,700,40))
                surface.blit(fonte_dialog.render(opt,True,BRANCO),(60,y))
            if answered:
                surface.blit(icon,(800,200+sel*60))
                if time.time()-t0>=1: break
            pygame.display.flip(); clock.tick(60)
    passou=acertos>=2
    msg = "Parabéns!" if passou else "Não foi dessa vez..."
    cor = (0,200,0) if passou else (200,0,0)
    t0=time.time()
    while time.time()-t0<2:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            
        surface.fill(PRETO)
        surface.blit(fonte_dialog.render(msg,True,cor),((LARGURA-300)//2,ALTURA//2))
        pygame.display.flip(); clock.tick(60)
    return passou

# ─── POSIÇÃO INICIAL ───
def ajustar_posicao_inicial(j,obs):
    while any(j.rect.colliderect(o.rect) for o in obs):
        j.rect.y-=j.speed
        if j.rect.top<=0:
            j.rect.top=0; j.rect.x+=j.speed
            if j.rect.right>=LARGURA:
                j.rect.right=LARGURA; break

# ─────────────────────────────────────────────
def main():


    # posição X fixa (centro)
    inv_x0 = (LARGURA - panel_w) // 2
    # quando oculto, Y fica abaixo da tela; quando visível, 10px acima da borda inferior
    inv_hidden_y  = ALTURA + 10
    inv_visible_y = ALTURA - panel_h - 10

    inv_current_y  = inv_hidden_y
    inv_target_y   = inv_hidden_y


    anim = load_animation_frames()
    jogador = Jogador(anim)
    grupo_jog = pygame.sprite.Group(jogador)

    natalie_sprite = load_npc_sprite("frame_13.png", scale=1.25)
    natalie = NPC(9*LARGURA/10, 1*ALTURA/10, natalie_sprite)

    # área da “Bola do ICEx” (região circular central)
    quest_target = pygame.Rect(LARGURA//2-60, ALTURA//2-60, 120,120)

    fases = [
        # 0 ── PORTARIA
        {
            "fundo"      : load_bg("portaria.png"),
            "obstaculos" : [],
            "placas"     : [],
            "itens"      : [],
            "npcs"       : [],
            "transicoes" : [       # <── NEW LIST
                { "rect": pygame.Rect(0, 0, LARGURA, 5),               # topo
                  "dest": 1,        # vai para bolajardim
                  "spawn_side": "bottom" }
            ]
        },

        # 1 ── BOLA/JARDIM
        {
            "fundo"      : load_bg("bolajardim.png"),
            "obstaculos" : [],
            "placas"     : [],
            "itens"      : [],
            "npcs"       : [],
            "quest_target": quest_target,
            "transicoes" : [
                { "rect": pygame.Rect(0, ALTURA-5, LARGURA, 5),        # base
                  "dest": 0,        # retorna à portaria
                  "spawn_side": "top" },

                { "rect": pygame.Rect(0, 0, LARGURA, 5),               # topo
                  "dest": 2,        # entra em salas1
                  "spawn_side": "bottom" }
            ]
        },

        # 2 ── SALAS 1
        {
            "fundo"      : load_bg("salas1.png"),
            "obstaculos" : [],
            "placas"     : [],
            "itens"      : [Item(700, 500, "Caneta")],
            "npcs"       : [natalie],
            "transicoes" : [
                { "rect": pygame.Rect(0, ALTURA-5, LARGURA, 5),        # base
                  "dest": 1,        # volta para bolajardim
                  "spawn_side": "top" }
            ]
        }
    ]

    fase_idx=0
    ajustar_posicao_inicial(jogador,fases[0]["obstaculos"])

    # --- variáveis de jogo/quest ---
    lendo_placa=False; texto_placa=""
    placa_prox=npc_prox=None
    quiz_pending=False
    evento_txt=""; evento_timer=0
    quest_state="not_started"     # → in_progress → photo_taken → done
    quest_msg_timer=0
    transition_cd,last_transition=1.0,0
    restart_to_menu=False

    rodando=True
    while rodando:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                snapshot=tela.copy()
                choice=__import__("main").tela_config(snapshot)
                if choice=="menu": restart_to_menu=True; rodando=False; break
            if ev.type==pygame.KEYDOWN:
                # placas
                if ev.key==pygame.K_e and placa_prox and not npc_prox:
                    lendo_placa=True; texto_placa=placa_prox.texto
                if ev.key==pygame.K_RETURN and lendo_placa:
                    lendo_placa=False
                # NPC natalie
                if ev.key==pygame.K_e and npc_prox and not npc_prox.ativo and not lendo_placa:
                    if quest_state == "not_started":
                        falas = [
                            "Natalie! Que bom que você está aqui, tenho uma prova agora,\n preciso muito de uma caneta emprestada…",
                            "Oi meu amor, eu tenho uma caneta da boa bem aqui, mas antes,\n preciso que você me ajude, tire uma foto bem bonita\n na bola do ICEx 📸",
                            "Depois, volte aqui e me mostre!",
                            "Ok, vou tirar a foto e já volto!",
                            "Ah, e não esquece de pegar a câmera na minha mochila!"]
                        npc_prox.iniciar_dialogo(falas)
                        jogador.coletar(Item(0, 0, "Camera"))   # ← NOVO ITEM
                        quest_state = "in_progress"

                    elif quest_state=="in_progress":
                        npc_prox.iniciar_dialogo(["Ainda não tirou a foto!"])
                    elif quest_state == "photo_taken":
                        falas = [
                            "Uau, ficou ótima!",
                            "Aqui está sua caneta 🖊️",
                            "Boa prova!"
                        ]
                        npc_prox.iniciar_dialogo(falas)
                        jogador.remover("Camera")               # ← PERDE câmera
                        jogador.coletar(Item(0, 0, "Caneta"))   # ← GANHA caneta
                        quest_state = "done"

                    else:
                        npc_prox.iniciar_dialogo(["Boa sorte na prova!"])
                elif ev.key==pygame.K_RETURN and npc_prox and npc_prox.ativo:
                    npc_prox.avancar_dialogo()
                # quiz
                if ev.key==pygame.K_q: quiz_pending=True
        if not rodando: break

        fase=fases[fase_idx]
        grupo_obs=pygame.sprite.Group(*fase["obstaculos"])
        grupo_pla=pygame.sprite.Group(*fase["placas"])
        grupo_itm=pygame.sprite.Group(*fase["itens"])
        grupo_npc=pygame.sprite.Group(*fase["npcs"])

        keys=pygame.key.get_pressed()
        if not (lendo_placa or quiz_pending or (npc_prox and npc_prox.ativo)):
            jogador.update(keys,fase["obstaculos"])

        # quest: checar foto
        # ─────── QUEST: tirar a foto manualmente ───────
        dentro_area_foto = (
            quest_state == "in_progress"
            and "quest_target" in fase
            and jogador.rect.colliderect(fase["quest_target"])
        )

        if dentro_area_foto and keys[pygame.K_f]:
            quest_state = "photo_taken"
            evento_txt = "📸 Foto tirada! Volte para Natalie."
            evento_timer = time.time()


        # transição de fase
        # ──────── TRANSIÇÕES ENTRE FASES ────────
        agora = time.time()
        # linhas verdes só para depuração – apague se quiser
        for tdata in fase["transicoes"]:
            pygame.draw.rect(tela, (0, 255, 0), tdata["rect"], 2)
            if jogador.rect.colliderect(tdata["rect"]) and agora - last_transition > transition_cd:
                last_transition = agora

                # índice do próximo mapa
                fase_idx = tdata["dest"]
                next_fase = fases[fase_idx]

                # onde o jogador deve aparecer no mapa de destino
                cx, cy = jogador.rect.center
                side = tdata["spawn_side"]
                if side == "top":
                    jogador.rect.midtop = (cx, 0)
                elif side == "bottom":
                    jogador.rect.midbottom = (cx, ALTURA)
                elif side == "left":
                    jogador.rect.midleft = (0, cy)
                elif side == "right":
                    jogador.rect.midright = (LARGURA, cy)

                ajustar_posicao_inicial(jogador, next_fase["obstaculos"])
                break         # evita múltiplas transições de uma vez

        # quiz
        if quiz_pending:
            res=run_quiz(tela)
            evento_txt="Evento A: Sucesso!" if res else "Evento B: Falha!"
            evento_timer=time.time(); quiz_pending=False

        # ---------- DRAW ----------
        tela.blit(fase["fundo"],(0,0))
        grupo_obs.draw(tela); grupo_itm.draw(tela)
        grupo_pla.draw(tela); grupo_npc.draw(tela); grupo_jog.draw(tela)

        # highlight quest target (debug / feedback)
        if quest_state=="in_progress" and "quest_target" in fase:
            pygame.draw.rect(tela,(255,255,0),fase["quest_target"],2)

        placa_prox=next((p for p in grupo_pla if jogador.rect.colliderect(p.rect.inflate(40,40))),None)
        npc_prox  =next((n for n in grupo_npc if jogador.rect.colliderect(n.rect.inflate(50,50))),None)

        # -------- prompt de interação --------
        if (placa_prox or npc_prox) and not lendo_placa and not (npc_prox and npc_prox.ativo):
            txt = "Pressione E para interagir"
            surf_txt  = fonte_dialog.render(txt, True, PRETO)
            w, h      = surf_txt.get_size()
            bg_rect   = pygame.Rect(0, 0, w + 20, h + 10)
            bg_rect.midbottom = (jogador.rect.centerx, jogador.rect.y - 10)
            
            box = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            box.fill((255, 255, 255, 200))
            tela.blit(box, bg_rect.topleft)
            pygame.draw.rect(tela, PRETO, bg_rect, 2)
            tela.blit(surf_txt, (bg_rect.x + 10, bg_rect.y + 5))
            
        # -------- dica de foto (quando dentro da área) --------
        if dentro_area_foto:
            txt = "Pressione F para tirar foto"
            surf_txt = fonte_dialog.render(txt, True, PRETO)
            w, h = surf_txt.get_size()
            bg_rect = pygame.Rect(0, 0, w + 20, h + 10)
            bg_rect.midbottom = (jogador.rect.centerx, jogador.rect.y - 50)

            box = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            box.fill((255, 255, 255, 200))
            tela.blit(box, bg_rect.topleft)
            pygame.draw.rect(tela, PRETO, bg_rect, 2)
            tela.blit(surf_txt, (bg_rect.x + 10, bg_rect.y + 5))



        # placa
        if lendo_placa:
            caixa=pygame.Rect(100,600,1000,150)
            tela.blit(pygame.transform.scale(WOOD_IMG,(caixa.width,caixa.height)),caixa.topleft)
            pygame.draw.rect(tela,PRETO,caixa,3)
            for i,linha in enumerate(texto_placa.split("\\n")):
                tela.blit(fonte_dialog.render(linha,True,PRETO),(caixa.x + 20, caixa.y + 20 + i * 30))

        # npc diálogo
        if npc_prox and npc_prox.ativo:
            caixa=pygame.Rect(80,580,1040,160)
            tela.blit(pygame.transform.scale(WOOD_IMG,(caixa.width,caixa.height)),caixa.topleft)
            pygame.draw.rect(tela,PRETO,caixa,3)
            linha = npc_prox.falas[npc_prox.idx]
            for i, parte in enumerate(linha.split("\n")):
                tela.blit(fonte_dialog.render(parte, True, PRETO),
                        (caixa.x + 20, caixa.y + 20 + i * 30))  # adjust spacing for large font


        desenhar_inventario(tela,jogador.inv)

        if evento_txt and time.time()-evento_timer<3:
            tela.blit(fonte_dialog.render(evento_txt,True,PRETO),
                      ((LARGURA-fonte_dialog.size(evento_txt)[0])//2,40))
        elif time.time()-evento_timer>=3: evento_txt=""

        ESC_FONT = pygame.font.Font("PressStart2P.ttf", 16)
        # desenha "Esc – Pausa/Config." com a fonte PressStart2P e borda preta
# desenha "Esc – Pausa/Config." com fonte 12px PressStart2P e borda preta
        txt = render_text_with_border("Esc – Pausa/Config.", BRANCO, PRETO, ESC_FONT, border_size=1)
        tela.blit(txt, (10, 10))


        pygame.display.flip()

    return "menu" if restart_to_menu else None

if __name__=="__main__":
    main()
