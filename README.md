# ICEx Odyssey: 
## A batalha pela aprovação

### Objetivos:
Este projeto propõe o desenvolvimento de um jogo 2d educativo e lúdico, ambientado no Instituto de Ciências Exatas (ICEx) da UFMG. O jogo oferece uma experiência interativa que permite explorar o prédio, seus laboratórios e professores icônicos. A proposta busca entreter e, ao mesmo tempo, ajudar especialmente os calouros a se familiarizarem com o espaço e a rotina acadêmica, promovendo curiosidade, engajamento e ambientação de forma divertida e envolvente.

### Features:
O jogo contará com a exploração detalhada do prédio do ICEx, permitindo ao jogador percorrer salas, corredores e laboratórios baseados na planta real da instituição. A narrativa envolverá eventos intrigantes e desafios que incentivam a investigação. Professores e figuras conhecidas do ICEx aparecerão como personagens interativos, fornecendo dicas ou participando da trama. O progresso dependerá da resolução de enigmas educativos ligados a conteúdos das disciplinas do instituto, como matemática, computação e física, promovendo aprendizado de forma leve e integrada. Tudo isso será envolto em uma ambientação visual e sonora imersiva, que reforça o clima assombroso do jogo.

### Equipe
- Arthur Buzelin Galery [Full-Stack]
- Arthur Rodrigues Chagas [Front-End]
- Pedro Augusto Torres Bento [Back-End]
- Yan Aquino Amorim [Full-Stack]

### Tecnologias
- Linguagem: Python
- Framework: Pygame

### Backlog do Produto
- **Como jogador, eu gostaria de controlar o personagem com as teclas de direção (esquerda, direita, pra cima etc...).**
- **Como jogador, eu gostaria de ver o personagem se movendo no cenário do ICEx da UFMG.**
- **Como jogador, eu gostaria de ter um objetivo no jogo, como alcançar um determinado ponto do mapa.**
- **Como jogador, eu gostaria de encontrar obstáculos no caminho, colisões, troca de cenário...**
- **Como jogador, eu gostaria de ouvir uma trilha sonora que se encaixe com o ambiente do ICEx.**
- **Como jogador, eu gostaria de ver uma tela de introdução com informações/configurações do jogo.**
- **Como jogador, eu gostaria que, ao atravessar a borda de um cenário, o jogo efetuasse a transição para o próximo mapa mantendo a posição relativa do personagem.**
- **Como jogador, eu gostaria que meu personagem não pudesse nascer (spawnar) em áreas de colisão, encontrando sempre um ponto livre.**
- **Como jogador, eu gostaria de interagir com NPCs (Natalie, Porteiro, Dexter) pressionando “E” dentro de uma zona de aproximação**
- **Como jogador, eu gostaria de poder pausar o jogo**



As tarefas foram distribuídas com base no planejamento do sprint, utilizando o método de Planning Poker para atribuição de Story Points. Cada membro da equipe recebeu tarefas proporcionais à sua experiência e ao nível de complexidade das atividades, garantindo um equilíbrio na carga de trabalho.

### Backlog do Sprint
#### Estrutura:
1. **Como jogador, eu gostaria de controlar o personagem com as teclas de direção (esquerda, direita, pra cima etc...).**
   
Implementar leitura de eventos de teclado para as setas direcionais.
Responsável: Rod

Mapear cada tecla de direção para alteração de posição do sprite.
Responsável: Buzelin

Ajustar velocidade e direção do personagem de acordo com a tecla pressionada.
Responsável: Pedro

Criar testes de movimentação e suavização de animação.
Responsável: Yan

2. **Como jogador, eu gostaria de ver o personagem se movendo no cenário do ICEx da UFMG.**

Integrar o sprite do personagem no cenário de fundo.
Responsável: Rod

Ajustar a ordem de desenho (z-ordering) para que o personagem apareça sobre o background.
Responsável: Buzelin

Carregar e organizar as animações de andar para as quatro direções.
Responsável: Pedro

Validar renderização contínua durante o frame loop.
Responsável: Yan

3. **Como jogador, eu gostaria de ter um objetivo no jogo, como alcançar um determinado ponto do mapa.**

Definir a posição e forma da “zona de objetivo” no mapa.
Responsável: Yan

Implementar detecção de colisão com a área de objetivo.
Responsável: Rod

Exibir uma notificação (“Objetivo alcançado!”) ao colidir com a zona.
Responsável: Pedro

Resetar ou avançar para o próximo estado/nível após alcançar o objetivo.
Responsável: Buzelin

4. **Como jogador, eu gostaria de encontrar obstáculos no caminho, colisões, troca de cenário...**

Carregar e associar máscaras de colisão pixel-a-pixel para cada cenário.
Responsável: Buzelin

Implementar verificação retangular + pixel-perfect contra essas masks.
Responsável: Rod

Criar sprites/obstáculos estáticos (paredes, mesas, etc.) no mundo.
Responsável: Pedro

Implementar transição de fase ao tocar áreas de troca de cenário.
Responsável: Yan

5. **Como jogador, eu gostaria de ouvir uma trilha sonora que se encaixe com o ambiente do ICEx.**

Selecionar e importar arquivos de áudio adequados (loop ambiental).
Responsável: Pedro

Implementar reprodução em loop usando pygame.mixer.
Responsável: Rod

Ajustar volume padrão e dinâmica de transição entre faixas.
Responsável: Yan

Adicionar opção de mute/unmute no menu de pausa/configuração.
Responsável: Buzelin

6. **Como jogador, eu gostaria de ver uma tela de introdução com informações/configurações do jogo.**

Criar layout do popup de intro com textura de madeira e fonte 16-bit.
Responsável: Yan

Implementar escurecimento do fundo enquanto o intro estiver visível.
Responsável: Pedro

Renderizar o texto de instruções com borda preta e fonte branca.
Responsável: Rod

Capturar tecla ou clique para fechar a intro e iniciar o jogo.
Responsável: Buzelin

7. **Como jogador, eu gostaria que, ao atravessar a borda de um cenário, o jogo efetuasse a transição para o próximo mapa mantendo a posição relativa do personagem.**

Detectar colisão do personagem com o retângulo de transição na borda.
Responsável: Rod

Calcular a posição de spawn no novo mapa baseado na “spawn_side”.
Responsável: Buzelin

Carregar e armazenar metadados de transição (destino e lado de entrada).
Responsável: Yan

Testar cenários de ida/volta sem glitch de teleporte.
Responsável: Pedro

8.**Como jogador, eu gostaria que meu personagem não pudesse nascer (spawnar) em áreas de colisão, encontrando sempre um ponto livre.**

Criar função que busca um ponto “branco” na máscara para spawn válido.
Responsável: Pedro

Ajustar a lógica inicial de spawn para usar essa função em vez de centro fixo.
Responsável: Rod

Escrever teste automático que valida spawn fora das áreas vermelhas.
Responsável: Yan

Atualizar ajustar_posicao_inicial para chamar o novo método de spawn.
Responsável: Buzelin

9. **Como jogador, eu gostaria de interagir com NPCs (Natalie, Porteiro, Dexter) pressionando “E” dentro de uma zona de aproximação.**

Definir retângulos de proximidade (inflation) em volta de cada NPC.
Responsável: Rod

Implementar lógica de captura de tecla “E” somente dentro dessa zona.
Responsável: Buzelin

Renderizar balão de diálogo com wood.png, fundo branco/translúcido e borda.
Responsável: Yan

Testar interações com Natalie, Porteiro e Dexter, garantindo fluxo de diálogo.
Responsável: Pedro

10. **Como jogador, eu gostaria de poder pausar o jogo.**
Criar flag paused e interceptar updates de lógica quando ativo.
Responsável: Rod

Exibir overlay de pausa com opções “Continuar” e “Menu” em wood.png.
Responsável: Pedro

Mapear tecla Esc para alternar entre pausado e rodando.
Responsável: Yan

Salvar estado corrente (posição, conhecimento, inventário) ao pausar e restaurar ao voltar.
Responsável: Buzelin

