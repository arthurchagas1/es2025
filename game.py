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
    fonte_dialog = pygame.font.Font(PIXEL_FONT, 20)
except FileNotFoundError:
    print("⚠️  Fonte PressStart2P não encontrada – usando sistema.")
    fonte_dialog = pygame.font.Font(None, 20)

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

# ───────── HUD INVENTÁRIO ─────────
def desenhar_inventario(surf,inv):
    x=LARGURA-50
    for nome,icon in reversed(inv):
        surf.blit(icon,(x,10))
        surf.blit(fonte_dialog.render(nome,True,PRETO),(x-110,15))
        x-=120

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
    anim = load_animation_frames()
    jogador = Jogador(anim)
    grupo_jog = pygame.sprite.Group(jogador)

    natalie_sprite = load_npc_sprite("frame_13.png", scale=1.25)
    natalie = NPC(LARGURA//2, ALTURA//2, natalie_sprite)

    # área da “Bola do ICEx” (região circular central)
    quest_target = pygame.Rect(LARGURA//2-60, ALTURA//2-60, 120,120)

    fases=[
        {"fundo":pygame.image.load("portaria.png").convert(),
         "obstaculos":[Obstaculo(300,200,200,50)],
         "placas":[Placa(600,300,40,40,"Bem-vindo à portaria!")],
         "itens":[],
         "npcs":[],
         "area_transicao":pygame.Rect(0,0,LARGURA,5),
         "transicao_direcao":"top"},
        {"fundo":pygame.image.load("bolajardim.png").convert(),
         "obstaculos":[Obstaculo(100,100,400,50)],
         "placas":[Placa(500,600,40,40,"Jardim central do ICEx.")],
         "itens":[],
         "npcs":[natalie],
         "area_transicao":pygame.Rect(0,ALTURA-5,LARGURA,5),
         "transicao_direcao":"bottom",
         "quest_target":quest_target}
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
                    if quest_state=="not_started":
                        falas=["Socorro? Precisa de caneta?",
                               "Faça o seguinte:",
                               "Tire uma foto na bola do ICEx 📸",
                               "Volte aqui depois!"]
                        npc_prox.iniciar_dialogo(falas)
                        quest_state="in_progress"
                    elif quest_state=="in_progress":
                        npc_prox.iniciar_dialogo(["Ainda não tirou a foto!"])
                    elif quest_state=="photo_taken":
                        falas=["Uau, ficou ótima!",
                               "Aqui está sua caneta 🖊️",
                               "Boa prova!"]
                        npc_prox.iniciar_dialogo(falas)
                        jogador.coletar(Item(0,0,"Caneta"))
                        quest_state="done"
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
        if quest_state=="in_progress" and "quest_target" in fase:
            if jogador.rect.colliderect(fase["quest_target"]):
                quest_state="photo_taken"
                evento_txt="📸 Foto tirada! Volte para Natalie."
                evento_timer=time.time()

        # transição de fase
        agora=time.time()
        if jogador.rect.colliderect(fase["area_transicao"]) and agora-last_transition>transition_cd:
            last_transition=agora; x0,y0=jogador.rect.center; dir0=fase["transicao_direcao"]
            fase_idx=(fase_idx+1)%len(fases); nova=fases[fase_idx]
            if dir0=="top": jogador.rect.midtop=(x0,ALTURA-jogador.rect.height)
            elif dir0=="bottom": jogador.rect.midbottom=(x0,0)
            ajustar_posicao_inicial(jogador,nova["obstaculos"])

        # quiz
        if quiz_pending:
            res=run_quiz(tela)
            evento_txt="Evento A: Sucesso!" if res else "Evento B: Falha!"
            evento_timer=time.time(); quiz_pending=False

        # ---------- DRAW ----------
        tela.blit(fase["fundo"],(0,0))
        grupo_obs.draw(tela); grupo_itm.draw(tela)
        grupo_pla.draw(tela); grupo_npc.draw(tela); grupo_jog.draw(tela)
        pygame.draw.rect(tela,(0,255,0),fase["area_transicao"],2)

        # highlight quest target (debug / feedback)
        if quest_state=="in_progress" and "quest_target" in fase:
            pygame.draw.rect(tela,(255,255,0),fase["quest_target"],2)

        placa_prox=next((p for p in grupo_pla if jogador.rect.colliderect(p.rect.inflate(40,40))),None)
        npc_prox  =next((n for n in grupo_npc if jogador.rect.colliderect(n.rect.inflate(50,50))),None)

        if (placa_prox or npc_prox) and not lendo_placa and not (npc_prox and npc_prox.ativo):
            tela.blit(fonte_dialog.render("Pressione E para interagir",True,PRETO),
                      (jogador.rect.x-80,jogador.rect.y-40))

        # placa
        if lendo_placa:
            caixa=pygame.Rect(100,600,1000,150)
            tela.blit(pygame.transform.scale(WOOD_IMG,(caixa.width,caixa.height)),caixa.topleft)
            pygame.draw.rect(tela,PRETO,caixa,3)
            for i,linha in enumerate(texto_placa.split("\\n")):
                tela.blit(fonte_dialog.render(linha,True,PRETO),(120,620+i*28))

        # npc diálogo
        if npc_prox and npc_prox.ativo:
            caixa=pygame.Rect(80,580,1040,160)
            tela.blit(pygame.transform.scale(WOOD_IMG,(caixa.width,caixa.height)),caixa.topleft)
            pygame.draw.rect(tela,PRETO,caixa,3)
            linha=npc_prox.falas[npc_prox.idx]
            tela.blit(fonte_dialog.render(linha,True,PRETO),(caixa.x+20,caixa.y+50))

        desenhar_inventario(tela,jogador.inv)

        if evento_txt and time.time()-evento_timer<3:
            tela.blit(fonte_dialog.render(evento_txt,True,PRETO),
                      ((LARGURA-fonte_dialog.size(evento_txt)[0])//2,40))
        elif time.time()-evento_timer>=3: evento_txt=""

        tela.blit(fonte_hud.render("Esc – Pausa/Config.",True,(255,255,0)),(10,10))
        pygame.display.flip()

    return "menu" if restart_to_menu else None

if __name__=="__main__":
    main()
