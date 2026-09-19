# Plano de Evolução — Jogo da Cobrinha

## 1. Objetivo

Evoluir o MVP atual para um jogo infantil, fofo e personalizável, mantendo as regras clássicas da cobrinha.

O jogador poderá:

- criar e escolher um perfil local;
- acumular moedas ao comer;
- comprar animais e comidas;
- escolher o animal e a comida usados na partida;
- navegar pelos menus com o mouse;
- jogar em tela cheia;
- manter seu progresso após fechar o jogo.

Todos os animais e comidas terão caráter exclusivamente visual. Eles não poderão alterar velocidade, pontuação, crescimento, colisões ou qualquer outra regra da partida.

---

## 2. Fluxo final do jogo

```text
Abrir o jogo
    ↓
Animação “Bem-vindo ao Jogo da Cobrinha”
    ↓
Escolher ou criar perfil
    ↓
Menu principal
    ├── PLAY
    │     ↓
    │   Partida
    │     ↓
    │   Game Over
    │     ├── Jogar novamente
    │     └── Voltar ao menu
    │
    └── STYLE
          ├── Animais
          └── Comidas
```

A animação de boas-vindas aparecerá sempre que o jogo for aberto e poderá ser pulada com qualquer clique ou tecla.

---

## 3. Regras de pontuação e moedas

O jogo terá dois valores diferentes:

- **Score:** pontuação da partida atual.
- **Moedas:** saldo permanente do perfil.

Cada comida ingerida concede:

- 1 ponto no score atual;
- 1 moeda para o perfil.

O score volta para zero quando uma nova partida começa.

As moedas permanecem salvas depois do Game Over, ao trocar de perfil e ao fechar o jogo.

Comprar um item desconta seu preço do saldo. Depois de comprado, o item permanece disponível para sempre naquele perfil.

Todos os tipos de comida concedem exatamente a mesma pontuação e quantidade de moedas.

---

## 4. Catálogo inicial

### 4.1 Animais

| Identificador | Animal | Preço |
|---|---|---:|
| `snake` | Cobra | Grátis |
| `worm` | Minhoca | 20 moedas |
| `caterpillar` | Lagarta | 40 moedas |
| `axolotl` | Axolote | 70 moedas |

### 4.2 Comidas

| Identificador | Comida | Preço |
|---|---|---:|
| `apple` | Maçã | Grátis |
| `strawberry` | Morango | 5 moedas |
| `cheese` | Queijo | 10 moedas |
| `cupcake` | Cupcake | 15 moedas |
| `pizza` | Pizza | 25 moedas |
| `sushi` | Sushi | 35 moedas |

Cada perfil novo começa com a cobra e a maçã adquiridas e equipadas.

Todos os demais itens aparecem desde o início na tela Style. Um item é considerado desbloqueado quando o jogador o compra.

---

## 5. Etapas de implementação

## 5.1 Etapa 008 — Tela cheia e tabuleiro responsivo

**Status:** concluída.

### Objetivo

Fazer o jogo ocupar a tela do computador sem alterar as regras da grade.

### Implementação

- Abrir o jogo em tela cheia usando a resolução atual do computador.
- Manter a grade lógica existente com 32 colunas e 24 linhas.
- Calcular o maior tamanho inteiro de célula que caiba na área disponível.
- Centralizar o tabuleiro na tela.
- Preencher o espaço ao redor com um fundo ilustrado.
- Adicionar uma borda decorativa com tema de jardim, folhas e formas arredondadas.
- Reservar uma área de interface para score, moedas e ações.
- Impedir que o animal ou a comida sejam renderizados fora do tabuleiro.
- Recalcular o layout quando a resolução mudar.
- Permitir alternância entre tela cheia e janela com `F11`.
- Usar uma janela redimensionável de 1280×800 como modo alternativo.
- Fazer `Esc` sair da tela cheia sem encerrar o jogo.
- Preservar velocidade, colisões, posições lógicas e regras existentes.

### Critérios de aceitação

- O jogo ocupa toda a tela ao iniciar.
- O tabuleiro aparece inteiro e centralizado.
- A proporção das células permanece quadrada.
- A grade continua tendo 32×24 células.
- O layout funciona em 1280×720, 1366×768 e 1920×1080.
- Alternar o modo de tela não reinicia a partida.

### Tarefas

- [x] Criar um modelo de layout responsivo.
- [x] Separar coordenadas lógicas de coordenadas visuais.
- [x] Adaptar as funções de renderização ao novo layout.
- [x] Implementar tela cheia e modo janela.
- [x] Criar a borda decorativa.
- [x] Adaptar o painel de score.
- [x] Adicionar testes de layout em diferentes resoluções.
- [x] Executar a validação completa.

---

## 5.2 Etapa 009 — Telas e navegação

**Status:** concluída.

### Objetivo

Adicionar o fluxo de boas-vindas, menu principal, tela Style e ações de Game Over.
A seleção de perfil permanece na Etapa 010.

### Estados da aplicação

A aplicação deverá possuir estados separados dos estados internos da partida:

- `WELCOME`
- `HOME`
- `STYLE`
- `PLAYING`
- `GAME_OVER`

Os estados `RUNNING` e `GAME_OVER` do domínio da partida continuarão existindo e não deverão controlar diretamente os menus.

### Animação de boas-vindas

- Mostrar o texto “Bem-vindo ao Jogo da Cobrinha”.
- Usar uma animação curta, com duração aproximada de dois segundos.
- Permitir que qualquer clique ou tecla pule a animação.
- Não usar pausas bloqueantes como `sleep`.
- Processar normalmente os eventos de fechamento durante a animação.

### Menu principal

O menu principal terá dois botões principais:

- `PLAY`
- `STYLE`

Também terá ações secundárias:

- sair do jogo.

### Componentes de interface

Criar componentes simples para:

- botões;
- abas de animais e comidas.

Os componentes deverão possuir estados visuais para:

- normal;
- mouse sobre o elemento;
- pressionado;
- selecionado;
- desabilitado.

### Controles

- O mouse controla os menus e as abas de Style.
- Setas e WASD continuam controlando o animal durante a partida.
- `R` e Enter continuam reiniciando depois do Game Over.
- O Game Over também terá botões para jogar novamente e voltar ao menu.

### Critérios de aceitação

- O jogo começa na animação de boas-vindas.
- A animação pode ser pulada.
- O jogador consegue navegar por todas as telas usando o mouse.
- O botão Play inicia uma partida.
- O botão Style abre a personalização.
- É possível voltar da tela Style ao menu.
- O Game Over permite jogar novamente ou voltar ao menu com o mouse.
- Fechar a janela encerra corretamente o pygame.

### Tarefas

- [x] Criar o controlador de estados da aplicação.
- [x] Implementar a tela de boas-vindas.
- [x] Implementar os componentes de botão.
- [x] Implementar o menu principal.
- [x] Implementar a estrutura da tela Style.
- [x] Implementar o overlay de Game Over.
- [x] Integrar eventos de mouse.
- [x] Preservar os controles atuais da partida.
- [x] Adicionar testes de navegação e clique.
- [x] Executar a validação completa.

---

## 5.3 Etapa 010 — Perfis locais e SQLite

**Status:** concluída.

### Objetivo

Salvar o progresso de diferentes jogadores no mesmo computador.

### Comportamento

- Depois da animação, o jogador sempre deverá escolher ou criar um perfil.
- Os perfis não terão senha.
- A seleção de perfil não representa autenticação de segurança.
- Cada perfil terá saldo, compras e estilos próprios.
- A troca de perfil deverá voltar à tela de seleção.
- A exclusão de perfis não fará parte desta etapa.

### Validação do nome

O nome do perfil deverá:

- ter entre 1 e 20 caracteres depois da remoção de espaços externos;
- não ser vazio;
- ser único sem diferenciar maiúsculas e minúsculas.

Exemplo: `Ana` e `ana` deverão ser considerados o mesmo nome.

### Armazenamento

Usar `sqlite3`, disponível na biblioteca padrão do Python.

O banco deverá ficar no diretório de dados do usuário:

- Linux: respeitar `XDG_DATA_HOME` ou usar `~/.local/share`;
- Windows: usar `LOCALAPPDATA`;
- macOS: usar `~/Library/Application Support`.

O caminho do banco deverá ser injetável para permitir testes com arquivos temporários.

### Estrutura inicial do banco

#### Tabela `schema_version`

- `version`

#### Tabela `profiles`

- `id`
- `name`
- `coins`
- `equipped_character`
- `equipped_food`
- `created_at`

#### Tabela `purchases`

- `profile_id`
- `item_type`
- `item_id`
- `purchased_at`

A combinação de perfil, tipo e item deverá ser única.

### Critérios de aceitação

- É possível criar mais de um perfil.
- Não é possível criar nomes duplicados.
- Cada perfil mantém seu próprio saldo.
- Compras e estilos permanecem após fechar e abrir o jogo.
- Um perfil novo começa com cobra e maçã.
- Os testes não escrevem no banco real do usuário.

### Tarefas

- [x] Criar o módulo de persistência.
- [x] Criar automaticamente o esquema do banco.
- [x] Implementar criação de perfil.
- [x] Implementar listagem e seleção de perfis.
- [x] Implementar carregamento do progresso.
- [x] Registrar cobra e maçã para perfis novos.
- [x] Implementar troca de perfil.
- [x] Criar a interface visual de seleção de perfil.
- [x] Adicionar testes com bancos temporários.
- [x] Executar a validação completa.

---

## 5.4 Etapa 011 — Moedas e compras

**Status:** concluída.

### Objetivo

Transformar as comidas ingeridas em moedas permanentes e permitir compras cosméticas.

### Evento de consumo

A lógica de domínio não deverá acessar o banco diretamente.

`Game.step()` deverá retornar um resultado que informe se o passo:

- realizou apenas movimento;
- consumiu uma comida;
- terminou em colisão.

A camada da aplicação usará o resultado de consumo para:

1. aumentar o saldo em memória;
2. salvar a moeda no banco;
3. atualizar a interface.

### Compra

Uma compra deverá ser executada em uma única transação SQLite:

1. carregar o saldo atual;
2. verificar se o item já foi comprado;
3. verificar se o saldo é suficiente;
4. descontar o preço;
5. registrar a compra;
6. confirmar a transação.

Se qualquer etapa falhar, nenhuma alteração deverá ser mantida.

### Resultados possíveis

- compra concluída;
- saldo insuficiente;
- item já adquirido;
- item inexistente;
- erro de persistência.

### Interface

O saldo de moedas deverá aparecer:

- no menu principal;
- na tela Style;
- durante a partida;
- no resumo do Game Over.

O resumo do Game Over deverá mostrar:

- score final;
- moedas obtidas na partida;
- saldo total.

### Critérios de aceitação

- Comer uma comida concede exatamente uma moeda.
- Movimentação normal não concede moedas.
- Colisões não concedem moedas.
- Reiniciar não duplica moedas.
- Fechar e reabrir o jogo preserva o saldo.
- Uma compra nunca deixa o saldo negativo.
- Uma compra repetida não desconta novamente.

### Tarefas

- [x] Criar o resultado tipado de `Game.step()`.
- [x] Adaptar os testes existentes ao resultado do passo.
- [x] Implementar crédito persistente de moedas.
- [x] Implementar transações de compra.
- [x] Mostrar saldo nas telas.
- [x] Mostrar moedas ganhas no Game Over.
- [x] Tratar falhas de persistência.
- [x] Adicionar testes de economia e transações.
- [x] Executar a validação completa.

---

## 5.5 Etapa 012 — Loja e estilos de comida

**Status:** concluída.

### Objetivo

Permitir comprar, equipar e usar diferentes aparências de comida.

### Tela Style

A aba de comidas deverá mostrar um cartão para cada item contendo:

- imagem;
- nome;
- preço;
- estado atual.

Estados possíveis:

- gratuito;
- disponível para compra;
- saldo insuficiente;
- adquirido;
- equipado.

### Interações

- Clicar em uma comida adquirida deverá equipá-la imediatamente.
- Clicar em uma comida ainda não adquirida deverá abrir uma confirmação.
- A confirmação deverá mostrar nome, preço e saldo restante.
- Itens sem saldo suficiente deverão continuar visíveis.
- A interface deverá informar claramente quando faltarem moedas.
- Somente uma comida poderá ficar equipada por vez.

### Renderização

- As comidas serão sprites cartoon em PNG com transparência.
- O sprite deverá ocupar aproximadamente 80% da célula.
- Todos os alimentos usarão a mesma área lógica e a mesma colisão.
- O alimento equipado será usado em todas as aparições durante a partida.
- Trocar a aparência não altera pontuação nem comportamento.

### Critérios de aceitação

- Todos os alimentos aparecem na loja.
- A maçã está disponível gratuitamente.
- Compras válidas permanecem salvas.
- O alimento equipado permanece selecionado após reabrir o jogo.
- Todos os alimentos concedem um ponto e uma moeda.
- O alimento nunca cobre células vizinhas.

### Tarefas

- [x] Criar os dados tipados do catálogo.
- [x] Implementar os cartões de comida.
- [x] Implementar confirmação de compra.
- [x] Implementar seleção de comida.
- [x] Criar os sprites da maçã, morango, queijo, cupcake, pizza e sushi.
- [x] Incluir os assets na instalação do pacote.
- [x] Adaptar a renderização da comida.
- [x] Adicionar testes de compra, seleção e renderização.
- [x] Executar a validação completa.

---

## 5.6 Etapa 013 — Animais fofinhos

### Objetivo

Substituir visualmente a cobra por diferentes animais sem alterar a jogabilidade.

### Estrutura visual

Cada animal deverá possuir sprites para:

- cabeça;
- corpo reto;
- curva;
- cauda.

A renderização deverá examinar os segmentos vizinhos para escolher:

- o tipo da parte;
- a direção;
- a rotação correta.

A posição lógica de cada segmento continuará sendo uma célula da grade.

### Direção artística

Os animais deverão ter estilo:

- cartoon;
- fofo;
- arredondado;
- colorido;
- reconhecível;
- apropriado para crianças.

Características visuais sugeridas:

- cobra verde com olhos grandes, escamas suaves e língua discreta;
- minhoca rosada com corpo macio e segmentado;
- lagarta verde com pequenas patas e antenas;
- axolote rosado com brânquias externas e pequenas patas.

### Prévia da tela Style

A prévia deverá usar os mesmos sprites da partida.

Cada animal será mostrado:

- com seis segmentos;
- com pelo menos uma curva;
- em tamanho maior que durante a partida;
- sobre um fundo que contraste com sua aparência.

Isso representa como o animal fica depois de comer três comidas.

### Regras compartilhadas

Todos os animais deverão:

- começar com três segmentos;
- crescer da mesma maneira;
- mover-se na mesma velocidade;
- possuir as mesmas colisões;
- receber a mesma pontuação;
- ocupar as mesmas células;
- não possuir poderes.

### Critérios de aceitação

- Todos os animais aparecem na tela Style.
- A cobra está disponível gratuitamente.
- Animais adquiridos podem ser equipados.
- O animal equipado aparece na próxima partida.
- Curvas, cabeça e cauda acompanham corretamente a direção.
- Nenhum animal altera as regras do domínio.

### Tarefas

- [x] Criar os cartões de animais.
- [x] Implementar compra e seleção de animal.
- [x] Identificar cabeça, corpo, curva e cauda na renderização.
- [x] Calcular a rotação de cada parte.
- [x] Criar os sprites dos quatro animais.
- [x] Implementar as prévias com seis segmentos.
- [x] Integrar o animal equipado à partida.
- [x] Adicionar testes das orientações dos segmentos.
- [x] Adicionar testes de equivalência das regras.
- [x] Executar a validação completa.

---

## 5.7 Etapa 014 — Acabamento e documentação

### Objetivo

Integrar as funcionalidades e preparar uma versão estável.

### Acabamento visual

- Usar uma paleta consistente em todas as telas.
- Usar tipografia legível e adequada para crianças.
- Manter contraste suficiente entre texto e fundo.
- Padronizar botões, cartões, margens e espaçamentos.
- Adicionar transições curtas entre telas.
- Evitar animações que impeçam cliques ou fechamento do jogo.
- Garantir que textos não sejam cortados em resoluções suportadas.

### Assets

Os arquivos de imagem deverão:

- usar PNG com transparência;
- ter nomes baseados nos identificadores do catálogo;
- ser armazenados dentro do pacote;
- ser incluídos na configuração de empacotamento;
- funcionar após instalação com `pip`;
- possuir origem e licença documentadas quando não forem originais.

### Erros

Falhas de leitura ou escrita deverão:

- ser capturadas;
- preservar o último estado válido conhecido;
- mostrar uma mensagem amigável;
- não apagar o banco;
- não encerrar o pygame sem limpeza.

### Documentação

Atualizar:

- `README.md`;
- `docs/PRODUCT.md`;
- instruções de controles;
- descrição de perfis;
- funcionamento das moedas;
- catálogo;
- persistência;
- modo tela cheia;
- estrutura de assets.

### Critérios de aceitação

- O fluxo completo funciona sem telas inacessíveis.
- Todos os assets aparecem após instalação limpa.
- O progresso continua válido depois de reiniciar o programa.
- O jogo funciona nos modos tela cheia e janela.
- Nenhum teste exige um monitor interativo.
- A documentação descreve o comportamento final.

### Tarefas

- [ ] Revisar todas as telas.
- [ ] Revisar o dimensionamento em diferentes resoluções.
- [ ] Revisar estados de hover, seleção e desabilitado.
- [ ] Revisar mensagens de erro.
- [ ] Confirmar inclusão dos assets no pacote.
- [ ] Atualizar README.
- [ ] Atualizar documentação de produto.
- [ ] Fazer revisão visual manual.
- [ ] Executar a validação completa.
- [ ] Revisar o diff final.

---

## 6. Organização sugerida do código

A estrutura final poderá seguir este formato:

```text
src/snake_game/
├── assets/
│   ├── animals/
│   ├── foods/
│   └── ui/
├── app.py
├── catalog.py
├── config.py
├── food.py
├── game.py
├── grid.py
├── layout.py
├── main.py
├── persistence.py
├── rendering.py
├── screens.py
├── snake.py
└── ui.py
```

Responsabilidades:

- `game.py`: regras da partida, score e eventos de consumo.
- `snake.py`: movimento, direção e corpo lógico.
- `persistence.py`: perfis, moedas, compras e SQLite.
- `catalog.py`: itens, preços e caminhos dos assets.
- `app.py`: estado geral da aplicação e navegação.
- `screens.py`: composição das telas.
- `ui.py`: botões, cartões e outros componentes.
- `layout.py`: cálculo responsivo de posições e dimensões.
- `rendering.py`: desenho do tabuleiro, animais, comidas e HUD.

A divisão deverá permanecer simples. Arquivos só deverão ser separados quando houver uma responsabilidade clara.

---

## 7. Estratégia de testes

### Domínio

Testar:

- score por comida;
- moeda por comida;
- ausência de recompensa em outros eventos;
- equivalência de regras entre animais;
- reinício de partida;
- colisões;
- crescimento.

### Persistência

Testar:

- criação do esquema;
- criação de perfil;
- nomes duplicados;
- saldo persistente;
- compras persistentes;
- compra atômica;
- saldo insuficiente;
- item duplicado;
- equipamento persistente;
- separação entre perfis.

### Interface

Testar:

- áreas clicáveis;
- hover;
- clique;
- navegação entre telas;
- animação pulável;
- seleção de perfil;
- confirmação de compra;
- tela de Game Over.

### Layout e renderização

Testar:

- cálculo do tamanho das células;
- centralização do tabuleiro;
- limites visuais;
- diferentes resoluções;
- rotação das partes dos animais;
- carregamento dos assets;
- renderização headless.

### Validação obrigatória

Ao final de cada etapa:

```bash
ruff check .
ruff format --check .
pytest
```

---

## 8. Decisões estabelecidas

- O progresso será local e armazenado em SQLite.
- Não haverá conta online, e-mail ou senha.
- O jogador escolherá um perfil sempre que abrir o jogo.
- A animação de boas-vindas aparecerá em toda execução e poderá ser pulada.
- O jogo abrirá em tela cheia adaptável.
- O mouse será usado nos menus.
- Setas e WASD continuarão controlando o animal.
- Os gráficos terão estilo cartoon fofo ilustrado.
- Os itens serão comprados diretamente com moedas.
- Todos os itens ficarão visíveis antes da compra.
- Compras gastarão moedas.
- Itens comprados serão permanentes.
- Somente um animal e uma comida poderão ficar equipados por vez.
- A prévia dos animais mostrará seis segmentos.
- Os estilos não terão efeitos sobre a jogabilidade.

---

## 9. Fora do escopo

Este plano não inclui:

- sincronização entre computadores;
- contas online;
- e-mail ou senha;
- banco de dados remoto;
- exclusão de perfis;
- recuperação de conta;
- ranking online;
- multiplayer;
- poderes;
- obstáculos;
- alimentos com pontuações diferentes;
- diferenças de velocidade entre animais;
- música ou efeitos sonoros;
- novos modos de jogo;
- controle do animal pelo mouse;
- loja com dinheiro real;
- microtransações.
