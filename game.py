import pygame, sys, os, time, random
from typing import List

pygame.init()
clock = pygame.time.Clock()

# ───────────────── CONSTANTES ─────────────────
LARGURA, ALTURA = 1200, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo 2D – itens + quiz + NPC")

BRANCO = (255,255,255)
CINZA  = (100,100,100)
PRETO  = (  0,  0,  0)
VERDE  = (  0,255,  0)
AZUL_CLARO = (150,200,255)

fonte      = pygame.font.SysFont("Arial", 24)
fonte_hud  = pygame.font.SysFont("Arial", 20)

# ────────────── ASSET HELPERS ────────────────
def load_animation_frames(folder="animacoes", scale=0.15):
    frames=[]
    for i in range(16):
        img=pygame.image.load(os.path.join(folder,f"frame_{i}.png")).convert_alpha()
        w,h=img.get_size()
        frames.append(pygame.transform.scale(img,(int(w*scale),int(h*scale))))
    return {"down":frames[0:4],"left":frames[8:12],
            "right":frames[12:16],"up":frames[4:8]}

def load_item_image(nome,size=(40,40)):
    path=os.path.join("itens",f"{nome}.png")
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(),size)
    surf=pygame.Surface(size,pygame.SRCALPHA); surf.fill((255,255,0))
    surf.blit(fonte.render(nome[0].upper(),True,PRETO),
              fonte.render(nome[0].upper(),True,PRETO).get_rect(center=(size[0]//2,size[1]//2)))
    return surf

def load_icon(path,color):
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(),(40,40))
    surf=pygame.Surface((40,40),pygame.SRCALPHA); surf.fill(color); return surf

ICON_OK   = load_icon("ok.png",(0,255,0))
ICON_FAIL = load_icon("fail.png",(255,0,0))

# ──────────────── SPRITES ───────────────────
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self,x,y,w,h):
        super().__init__()
        self.image=pygame.Surface((w,h)); self.image.fill(CINZA)
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
        self.nome=nome
        self.image=load_item_image(nome)
        self.rect=self.image.get_rect(topleft=(x,y))

class Jogador(pygame.sprite.Sprite):
    def __init__(self,anim):
        super().__init__()
        self.anim=anim; self.dir="down"; self.idx=0; self.speed=5
        self.image=anim["down"][0]
        self.rect=self.image.get_rect(center=(LARGURA//2,ALTURA//2))
        self.inv:List[tuple[str,pygame.Surface]]=[]
    def coletar(self,it:Item):
        if it.nome not in [n for n,_ in self.inv]:
            self.inv.append((it.nome,it.image))
    def update(self,keys,obsts):
        old=self.rect.copy(); moving=False
        if keys[pygame.K_LEFT]:  self.rect.x-=self.speed; self.dir="left"; moving=True
        elif keys[pygame.K_RIGHT]:self.rect.x+=self.speed; self.dir="right";moving=True
        elif keys[pygame.K_UP]:  self.rect.y-=self.speed; self.dir="up";   moving=True
        elif keys[pygame.K_DOWN]:self.rect.y+=self.speed; self.dir="down"; moving=True
        for o in obsts:
            if self.rect.colliderect(o.rect): self.rect=old; break
        self.rect.clamp_ip(pygame.Rect(0,0,LARGURA,ALTURA))
        self.idx=(self.idx+0.15)%len(self.anim[self.dir]) if moving else 0
        self.image=self.anim[self.dir][int(self.idx)]

class NPC(pygame.sprite.Sprite):
    def __init__(self,anim,x,y):
        super().__init__()
        self.anim=anim; self.dir="down"; self.idx=0
        self.image=anim["down"][0]
        self.rect=self.image.get_rect(center=(x,y))
    def update(self):
        self.idx=(self.idx+0.05)%len(self.anim[self.dir])
        self.image=self.anim[self.dir][int(self.idx)]

# ─────────────── INVENTÁRIO HUD ───────────────
def desenhar_inventario(surface,inv):
    x=LARGURA-50
    for nome,ico in reversed(inv):
        surface.blit(ico,(x,10))
        surface.blit(fonte.render(nome,True,PRETO),(x-110,15)); x-=120

# ─────────────── QUIZ UTILITIES ───────────────
class QuizQuestion:
    def __init__(self,q,opts,ans): self.q=q; self.opts=opts; self.ans=ans

QUESTOES=[
    QuizQuestion("Quanto é 2 + 2?",["3","4","5","22"],1),
    QuizQuestion("Qual linguagem estamos usando?",["Java","C++","Python","Ruby"],2),
    QuizQuestion("Qual planeta é conhecido como o Planeta Vermelho?",["Terra","Vênus","Marte","Júpiter"],2),
    QuizQuestion("Quem pintou a Mona Lisa?",["Van Gogh","Da Vinci","Picasso","Michelangelo"],1),
    QuizQuestion("Em que continente fica o Brasil?",["África","Europa","Ásia","América do Sul"],3),
]

def run_quiz(surface,font)->bool:
    perguntas=random.sample(QUESTOES,3); acertos=0
    for q in perguntas:
        sel,resp,icon,t0=0,False,None,0
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN and not resp:
                    if e.key in (pygame.K_UP,pygame.K_w): sel=(sel-1)%len(q.opts)
                    elif e.key in (pygame.K_DOWN,pygame.K_s): sel=(sel+1)%len(q.opts)
                    elif e.key==pygame.K_RETURN:
                        resp=True; ok=(sel==q.ans)
                        icon=ICON_OK if ok else ICON_FAIL
                        if ok: acertos+=1; t0=time.time()
            surface.fill((30,30,90))
            surface.blit(font.render(q.q,True,BRANCO),(60,80))
            for i,opt in enumerate(q.opts):
                y=200+i*60
                if i==sel: pygame.draw.rect(surface,AZUL_CLARO,(50,y-5,700,40))
                surface.blit(font.render(opt,True,BRANCO),(60,y))
            if resp:
                surface.blit(icon,(800,200+sel*60))
                if time.time()-t0>=1: break
            pygame.display.flip(); clock.tick(60)
    passou=acertos>=2
    msg="Parabéns! Você passou." if passou else "Não foi dessa vez..."
    cor=(0,200,0) if passou else (200,0,0)
    t0=time.time()
    while time.time()-t0<2:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        surface.fill(PRETO)
        surface.blit(font.render(msg,True,cor),((LARGURA-300)//2,ALTURA//2))
        pygame.display.flip(); clock.tick(60)
    return passou

# ─────────── POSIÇÃO INICIAL ────────────
def ajustar_posicao_inicial(jogador,obstaculos):
    while any(jogador.rect.colliderect(o.rect) for o in obstaculos):
        jogador.rect.y-=jogador.speed
        if jogador.rect.top<=0:
            jogador.rect.top=0; jogador.rect.x+=jogador.speed
            if jogador.rect.right>=LARGURA:
                jogador.rect.right=LARGURA; break

# ───────────────── MAIN LOOP ─────────────
def main():
    # animações
    anim_player  = load_animation_frames("animacoes")
    anim_natalie = load_animation_frames("animacoes2")

    jogador = Jogador(anim_player)
    natalie = NPC(anim_natalie, LARGURA//2, ALTURA//2)  # centro do jardim

    fases=[
        {"fundo":pygame.image.load("portaria.png").convert(),
         "obstaculos":[Obstaculo(300,200,200,50)],
         "placas":[Placa(600,300,40,40,"Bem-vindo à portaria!")],
         "itens":[Item(400,500,"Chave")],
         "npcs":[],
         "area_trans":pygame.Rect(0,0,LARGURA,5),
         "dir":"top"},
        {"fundo":pygame.image.load("bolajardim.png").convert(),
         "obstaculos":[Obstaculo(100,100,400,50)],
         "placas":[Placa(500,600,40,40,"Aqui é o jardim central.")],
         "itens":[],
         "npcs":[natalie],
         "area_trans":pygame.Rect(0,ALTURA-5,LARGURA,5),
         "dir":"bottom"}
    ]

    fase_idx=0
    ajustar_posicao_inicial(jogador,fases[0]["obstaculos"])

    grupo_jog=pygame.sprite.Group(jogador)
    grupo_npc=pygame.sprite.Group()

    lendo_placa=False; texto_placa=""
    placa_prox=None; npc_prox=None
    quest_started=False; quest_done=False
    bola_area=pygame.Rect(540,280,120,120)  # ajuste se necessário
    quiz_pending=False; evento_txt=""; evento_timer=0
    transition_cd,last_transition=1.0,0
    restart_to_menu=False

    rodando=True
    while rodando:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                snapshot=tela.copy()
                import sys,importlib
                main_mod=sys.modules["main"]
                choice=main_mod.tela_config(snapshot)
                if choice=="menu": restart_to_menu=True; rodando=False
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_e and placa_prox:
                    lendo_placa=True; texto_placa=placa_prox.texto
                if ev.key==pygame.K_RETURN and lendo_placa:
                    lendo_placa=False
                if ev.key==pygame.K_e and npc_prox==natalie and not quest_started:
                    quest_started=True
                    evento_txt="Natalie: Tire uma foto da bola! (aperte F lá)"
                    evento_timer=time.time()
                if ev.key==pygame.K_f and quest_started and not quest_done:
                    if jogador.rect.colliderect(bola_area):
                        quest_done=True
                        evento_txt="Natalie: Obrigada! :)"
                        evento_timer=time.time()
                if ev.key==pygame.K_q:
                    quiz_pending=True

        if restart_to_menu: break

        fase=fases[fase_idx]
        grupo_obs=pygame.sprite.Group(*fase["obstaculos"])
        grupo_pla=pygame.sprite.Group(*fase["placas"])
        grupo_itm=pygame.sprite.Group(*fase["itens"])
        grupo_npc=pygame.sprite.Group(*fase["npcs"])

        keys=pygame.key.get_pressed()
        if not lendo_placa and not quiz_pending:
            jogador.update(keys,fase["obstaculos"])
        grupo_npc.update()

        # coleta item
        it_hit=pygame.sprite.spritecollideany(jogador,grupo_itm)
        if it_hit: jogador.coletar(it_hit); grupo_itm.remove(it_hit)

        # transição
        now=time.time()
        if jogador.rect.colliderect(fase["area_trans"]) and now-last_transition>transition_cd:
            last_transition=now
            x0,y0=jogador.rect.center; dir0=fase["dir"]
            fase_idx=(fase_idx+1)%len(fases); fase=fases[fase_idx]
            if dir0=="top": jogador.rect.midtop=(x0,ALTURA-jogador.rect.height)
            elif dir0=="bottom": jogador.rect.midbottom=(x0,0)
            ajustar_posicao_inicial(jogador,fase["obstaculos"])

        # quiz
        if quiz_pending:
            ok=run_quiz(tela,fonte)
            evento_txt="Evento A: Sucesso!" if ok else "Evento B: Falha!"
            evento_timer=time.time(); quiz_pending=False

        placa_prox=next((p for p in grupo_pla if jogador.rect.colliderect(p.rect.inflate(40,40))),None)
        npc_prox  =next((n for n in grupo_npc if jogador.rect.colliderect(n.rect.inflate(60,60))),None)

        # ───── DRAW ─────
        tela.blit(fase["fundo"],(0,0))
        grupo_obs.draw(tela); grupo_itm.draw(tela); grupo_pla.draw(tela)
        grupo_npc.draw(tela); grupo_jog.draw(tela)
        pygame.draw.rect(tela,(0,255,0),fase["area_trans"],2)
        if fase_idx==1:
            pygame.draw.rect(tela,(255,255,0),bola_area,2)  # debug visor

        if placa_prox and not lendo_placa:
            tela.blit(fonte.render("E para ler placa",True,PRETO),
                      (jogador.rect.x-40,jogador.rect.y-30))
        if npc_prox==natalie and not quest_started:
            tela.blit(fonte.render("E para falar com Natalie",True,PRETO),
                      (jogador.rect.x-60,jogador.rect.y-40))

        if lendo_placa:
            caixa=pygame.Rect(100,600,1000,150)
            pygame.draw.rect(tela,BRANCO,caixa); pygame.draw.rect(tela,PRETO,caixa,3)
            for i,l in enumerate(texto_placa.split("\\n")):
                tela.blit(fonte.render(l,True,PRETO),(120,620+i*30))

        desenhar_inventario(tela,jogador.inv)

        if quest_started:
            status="concluída" if quest_done else "pendente"
            tela.blit(fonte_hud.render(f"Tarefa: Foto da bola — {status}",True,(255,215,0)),(10,40))

        if evento_txt and time.time()-evento_timer<3:
            tela.blit(fonte.render(evento_txt,True,PRETO),
                      ((LARGURA-fonte.size(evento_txt)[0])//2,70))
        elif time.time()-evento_timer>=3:
            evento_txt=""

        tela.blit(fonte_hud.render("Esc – Configurações",True,(255,255,0)),(10,10))
        pygame.display.flip()

    if restart_to_menu: return "menu"
    return None

if __name__=="__main__":
    main()
