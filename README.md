# ICEx Odyssey: 
## A batalha pela aprovação

### Objetivos:
Este projeto propõe o desenvolvimento de um jogo de plataforma 2d educativo e lúdico, ambientado no Instituto de Ciências Exatas (ICEx) da UFMG. Com elementos de suspense e mistério, o jogo oferece uma experiência interativa que permite explorar o prédio, seus laboratórios e professores icônicos. A proposta busca entreter e, ao mesmo tempo, ajudar especialmente os calouros a se familiarizarem com o espaço e a rotina acadêmica, promovendo curiosidade, engajamento e ambientação de forma divertida e envolvente.

### Features:
O jogo contará com a exploração detalhada do prédio do ICEx, permitindo ao jogador percorrer salas, corredores e laboratórios baseados na planta real da instituição. A narrativa envolverá uma atmosfera de suspense e mistério, com eventos intrigantes e desafios que incentivam a investigação. Professores e figuras conhecidas do ICEx aparecerão como personagens interativos, fornecendo dicas ou participando da trama. O progresso dependerá da resolução de enigmas educativos ligados a conteúdos das disciplinas do instituto, como matemática, computação e física, promovendo aprendizado de forma leve e integrada. Tudo isso será envolto em uma ambientação visual e sonora imersiva, que reforça o clima assombroso do jogo.

### Equipe
- Arthur Buzelin Galery [Full-Stack]
- Arthur Rodrigues Chagas [Front-End]
- Pedro Augusto Torres Bento [Back-End]
- Yan Aquino Amorim [Full-Stack]

As tarefas foram distribuídas com base no planejamento do sprint, utilizando o método de Planning Poker para atribuição de Story Points. Cada membro da equipe recebeu tarefas proporcionais à sua experiência e ao nível de complexidade das atividades, garantindo um equilíbrio na carga de trabalho.

### Backlog do Produto
- **Como jogador, eu gostaria de controlar o personagem com as teclas de direção (esquerda, direita, pular).**
- **Como jogador, eu gostaria de ver o personagem se movendo no cenário do ICEx da UFMG.**
- **Como jogador, eu gostaria de ter um objetivo no jogo, como alcançar um determinado ponto do mapa.**
- **Como jogador, eu gostaria de encontrar obstáculos no caminho, como plataformas ou buracos.**
- **Como jogador, eu gostaria de ouvir uma trilha sonora que se encaixe com o ambiente do ICEx.**
- **Como jogador, eu gostaria de ver uma tela de introdução com informações sobre o jogo.**
- **Como jogador, eu gostaria de ver uma tela de fim de jogo que mostre minha pontuação ou desempenho.**
- **Como desenvolvedor, eu gostaria de poder testar a física do personagem para garantir que o movimento e os saltos sejam naturais.**
- **Como desenvolvedor, eu gostaria de poder adicionar novos níveis com diferentes desafios e obstáculos.**
- **Como desenvolvedor, eu gostaria de poder criar e alterar os gráficos do cenário para incluir detalhes do ICEx.**
- **Como desenvolvedor, eu gostaria de ter uma tela de pause para que o jogador possa interromper o jogo.**
- **Como administrador, eu gostaria de gerenciar os níveis do jogo, incluindo a criação e exclusão de níveis.**
- **Como administrador, eu gostaria de poder monitorar o desempenho do jogo, como o tempo de carregamento e a estabilidade.**

### Backlog do Sprint
#### Estrutura:
**Eu, como jogador, gostaria de controlar um personagem que se move e pula.**
- Implementar a movimentação básica do personagem (esquerda/direita) [Responsável: Arthur B.][3]
- Implementar o pulo do personagem [Responsável: Arthur C.][5]
- Implementar a detecção de colisões com o solo [Responsável: Yan][5]

**Eu, como jogador, gostaria de ter obstáculos e inimigos no cenário.**
- Implementar plataformas e obstáculos estáticos [Responsável: Pedro][2]
- Implementar inimigos com movimento básico [Responsável: Arthur B.][5]
- Implementar colisões entre personagem e inimigos [Responsável: Pedro][8]

**Eu, como jogador, gostaria de ter um sistema de pontuação e níveis no jogo.**
- Implementar o sistema de pontuação [Responsável: Pedro][3]
- Implementar a transição entre níveis [Responsável: Arthur C.][5]
- Adicionar aumento de dificuldade ao progredir de nível [Responsável: Yan][8]

**Eu como aluno da UFMG, gostaria de explorar o ICEx e seus laboratórios de forma divertida e interativa, enquanto enfrento desafios que me ensinem sobre a rotina acadêmica.**
- Implementar o mapa interativo do ICEx com locais como laboratórios, salas de aula e áreas comuns [Responsável: Yan][2]
- Criar uma mecânica de exploração com dicas e mensagens ocultas espalhadas pelo campus [Responsável: Arthur C.][5]
- Adicionar NPCs representando professores e funcionários do ICEx que forneçam desafios e informações sobre a rotina acadêmica [Responsável: Arthur B.][3]
