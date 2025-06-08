# Vult - A 2D Medieval-Themed Adventure Game

## Description
Vult is a 2D medieval-themed adventure game developed in Python using the Pygame library. It features a player character exploring a tile-based world, interacting with NPCs through a dialogue system, and navigating with a player-following camera.

## Features
*   **Player Character:** Controllable player with 4-directional movement and sprites. Animation occurs when moving.
*   **NPCs:** Stationary Non-Player Characters that can trigger dialogue upon collision. NPCs can have idle animations.
*   **Camera System:** Player-following camera that keeps the player centered on the screen.
*   **Animation:** Simple 2-frame animation system for characters.
*   **Tile-Based Map:** Game world built from a `.map` file defining tile layouts, with a base background image.
*   **Collision Detection:** Tile-based collision system. Player collision is primarily based on the lower part of the sprite (feet).
*   **Dialogue System:** Interactive dialogue with NPCs, progressing with spacebar and exiting with ESC.

## Project Structure
The project is organized as follows:
```
vult/
├── README.md
├── env/                  # Virtual environment
├── src/
│   ├── main.py           # Main entry point of the game
│   ├── game.py           # Core game logic, event handling, game loop
│   ├── character.py      # Player and NPC character classes, movement, animation
│   ├── camera.py         # Camera logic
│   ├── dialogue_system.py # Handles dialogue interactions
│   ├── story.py          # Contains dialogue content for NPCs
│   ├── config.py         # Game configuration (screen size, tile size, etc.)
│   └── assets/
│       ├── map_layout.map  # Defines the tile structure of the game map
│       ├── map_image.png   # Base background image for the map
│       ├── *.png           # Sprite sheets and tile images
│       └── ...             # Other assets
└── VISUAL_NOVEL_GUIDE.md # (Informational guide, not part of the core game)
```

## Setup and Installation

### Prerequisites
*   Python 3.x (the project uses Python 3.12)
*   Pygame library

### Steps
1.  **Clone the repository (if applicable) or ensure you have the project files.**
    If you have the project, navigate to its root directory (e.g., `vult/`).

2.  **Set up the virtual environment:**
    The project includes an `env` directory. To use it, activate it:
    *   On macOS/Linux:
        ```bash
        source env/bin/activate
        ```
    *   On Windows:
        ```bash
        .\env\Scripts\activate
        ```
    If you need to recreate it or set it up from scratch:
    ```bash
    python3 -m venv env
    source env/bin/activate # or .\env\Scripts\activate for Windows
    ```

3.  **Install dependencies:**
    The primary dependency is Pygame. Ensure your virtual environment is active, then run:
    ```bash
    pip install pygame
    ```

## How to Run
1.  Make sure your virtual environment is activated.
2.  Navigate to the `src` directory from the project root:
    ```bash
    cd src
    ```
3.  Run the `main.py` script:
    ```bash
    python main.py
    ```
    Alternatively, from the project root directory:
    ```bash
    python src/main.py
    ```

## Configuration
Key game configurations can be found and modified in `src/config.py`. This includes:
*   Screen dimensions (`SCREEN_WIDTH`, `SCREEN_HEIGHT`)
*   Tile size (`TILE_SIZE`)
*   Player speed (`PLAYER_SPEED`)
*   Animation frame rate (`ANIMATION_FRAME_RATE`)

Sprite paths, character dimensions, and collision box ratios are primarily managed within `src/character.py` and utilized by `src/game.py`.
The map layout is defined in `src/assets/map_layout.map`.
Character sprites and other visual assets are located in `src/assets/`.

## Gameplay Controls
*   **Arrow Keys (Up, Down, Left, Right):** Move the player character.
*   **Spacebar:** Advance dialogue when interacting with NPCs.
*   **ESC (Escape Key):** Exit dialogue.

## Current Status & Next Steps (as of last update)
*   The game is runnable with core mechanics implemented (movement, collision, dialogue, animation).
*   Sprite scaling (28x34 sprites scaled to 58x81 on map) and feet-based collision are in place.
*   **Pending Verification:** Confirm that sand tiles (`'s'`) are correctly non-blocking with the new feet-based collision.
*   **Pending Testing:** Thoroughly test game stability, character movement across different tile types, collision robustness, and dialogue interactions.

# Jogo Medieval 2D em Pygame

Este é um jogo 2D de temática medieval desenvolvido em Python com a biblioteca Pygame. O projeto inclui um sistema de câmera que segue o jogador, NPCs estacionários com diálogo, animação de personagens, um mapa baseado em tiles carregado de um arquivo `.map`, e colisão baseada em tiles.

## Configuração e Execução

### Pré-requisitos

*   Python 3.x
*   Pygame

### Instalação de Dependências

1.  Certifique-se de que o Python está instalado.
2.  Instale o Pygame. Se você tiver um arquivo `requirements.txt` (não fornecido neste projeto base, mas comum), você pode usar:
    ```bash
    pip install -r requirements.txt
    ```
    Caso contrário, instale o Pygame diretamente:
    ```bash
    pip install pygame
    ```

### Executando o Jogo

Para iniciar o jogo, navegue até o diretório raiz do projeto no terminal e execute:

```bash
python src/main.py
```
ou, se estiver no diretório `src/`:
```bash
python main.py
```
Pode ser necessário ajustar o PYTHONPATH ou a forma como os módulos são importados dependendo de como você estrutura seu ambiente e executa o script. A forma mais garantida a partir da raiz do projeto (`/home/ricardosousa339/projects/vult`) é:
```bash
python /home/ricardosousa339/projects/vult/src/main.py
```

## Estrutura do Projeto

*   `src/`: Contém todo o código fonte do jogo.
    *   `main.py`: Ponto de entrada principal do jogo. Inicializa e executa o objeto `Game`.
    *   `game.py`: Classe principal `Game` que gerencia o loop do jogo, estados (mapa, diálogo), eventos, atualizações e renderização.
    *   `character.py`: Classe `Character` para o jogador e NPCs, lidando com movimento, animação e sprites.
    *   `camera.py`: Classe `Camera` para gerenciar a visão do jogo que segue o jogador.
    *   `dialogue_system.py`: Classe `DialogueSystem` para exibir caixas de diálogo e texto.
    *   `story.py`: Classe `Story` para gerenciar as cenas de diálogo dos NPCs.
    *   `config.py`: Contém constantes globais como dimensões da tela, FPS, cores, e dimensões do mapa.
    *   `assets/`: Contém todos os assets do jogo.
        *   `map_layout.map`: Arquivo de texto que define o layout do mapa do jogo.
        *   Imagens de sprites (ex: `sprite_knight_frente.png`, `grama_tile_0.png`, `map_image.png`).
        *   Arquivos com sufixo `:Zone.Identifier` são metadados do Windows e podem ser ignorados ou removidos se não estiverem em uso.

## Configuração do Mapa (`map_layout.map`)

O arquivo `src/assets/map_layout.map` é um arquivo de texto simples que define a disposição dos tiles no mapa do jogo.

### Formato

*   Cada linha no arquivo representa uma linha de tiles no mapa.
*   Cada "palavra" (separada por espaços) em uma linha representa um tile.
*   As dimensões do mapa (número de tiles em largura e altura) são inferidas a partir deste arquivo. A imagem de fundo (`map_image.png`) e as constantes `MAP_WIDTH` e `MAP_HEIGHT` em `config.py` devem estar em harmonia com o número de tiles e `tile_size`.

### Chaves de Tiles

As seguintes chaves de tiles são usadas no `game.py` e devem corresponder às imagens em `src/assets/`:

*   `g0`: Tile de grama (rotação 0).
*   `g90`: Tile de grama (rotação 90).
*   `g180`: Tile de grama (rotação 180).
*   `g270`: Tile de grama (rotação 270).
*   `s`: Tile de areia (passável).
*   `x`: Tile transparente/placeholder (usado para colisão, geralmente invisível mas bloqueador). Outras chaves podem ser adicionadas para diferentes tipos de tiles.

### Colisão de Tiles

*   A colisão é definida na classe `Game` na lista `self.blocking_tile_keys`.
*   Atualmente, as chaves `['x', 'g0', 'g90', 'g180', 'g270']` são consideradas bloqueadoras.
*   Tiles com a chave `'s'` (areia) são passáveis.
*   O tamanho de cada tile no jogo é definido por `self.tile_size` na classe `Game` (atualmente 100 pixels).

### Imagem de Fundo do Mapa

*   Uma imagem de fundo base (`map_image.png`) é carregada e desenhada primeiro.
*   Os tiles do `map_layout.map` são desenhados sobre esta imagem.
*   As dimensões desta imagem devem corresponder a `MAP_WIDTH` e `MAP_HEIGHT` em `config.py`.

## Programação e Manutenção

### Personagens (`character.py`)

*   **Sprites e Animação**:
    *   Os caminhos para os sprites do jogador são definidos em `player_sprite_paths` na classe `Game`. Espera-se um dicionário com chaves como "frente", "costas", "esquerda", "direita".
    *   Os NPCs usam `npc_sprite_paths` de forma similar, mas podem ter um conjunto mais simples de sprites (ex: apenas "frente").
    *   A animação é de 2 frames. As imagens de sprite devem ser uma folha de sprites horizontal com os dois frames lado a lado. O código em `Character.__init__` divide a imagem carregada ao meio para obter os dois frames. Se um sprite tiver apenas um frame (largura não é o dobro da altura de um frame individual), ele é tratado como um sprite de frame único.
    *   O jogador anima apenas quando está se movendo (`self.is_moving = True`). NPCs podem ser configurados para animar continuamente se tiverem mais de um frame e `is_moving` for definido como `True` para eles (atualmente, NPCs com múltiplos frames animam por padrão no loop de update do `Game`).
*   **Dimensões do Sprite no Mapa**:
    *   `self.map_sprite_width` e `self.map_sprite_height` na classe `Character` definem o tamanho do personagem quando desenhado no mapa. Ajuste estes valores para manter a proporção correta do seu sprite (ex: se o sprite original é 28x34, mantenha essa proporção ao escalar).
*   **Dimensões do Sprite no Diálogo**:
    *   `self.dialogue_sprite_original_width` e `self.dialogue_sprite_original_height` na classe `Character` são automaticamente definidos a partir das dimensões do primeiro frame do sprite "frente" carregado. Estes são usados para desenhar o personagem durante as cenas de diálogo.
*   **Hitbox de Colisão**:
    *   Para colisões com tiles, o personagem usa uma hitbox menor que representa seus pés, permitindo que a parte superior do corpo se sobreponha visualmente aos obstáculos.
    *   `self.collision_box_width_ratio` e `self.collision_box_height_ratio` controlam o tamanho desta hitbox em relação ao tamanho total do sprite no mapa.
    *   `self.collision_box_offset_x` e `self.collision_box_offset_y` posicionam esta hitbox na parte inferior central do sprite.

### NPCs e Diálogo (`game.py`, `story.py`)

*   **Adicionando NPCs**:
    1.  Defina os caminhos dos sprites para o novo NPC em `npc_sprite_paths` (ou crie um novo dicionário de caminhos se for específico).
    2.  Instancie um novo objeto `Character` no dicionário `self.npcs` na classe `Game`. Forneça nome, cor (fallback), posição inicial no mapa (`map_x`, `map_y`) e os caminhos dos sprites.
    3.  Adicione o NPC ao dicionário `self.characters`.
*   **Criando Diálogos**:
    1.  Crie um objeto `Story`.
    2.  Defina a lista `story.scenes`. Cada cena é um dicionário com:
        *   `"background"`: (Atualmente não usado para mudar o fundo da cena de diálogo, mas presente na estrutura).
        *   `"character"`: A chave do personagem (do dicionário `self.characters`) que está falando.
        *   `"text"`: A string de diálogo.
    3.  Atribua o objeto `Story` ao atributo `story` do NPC (ex: `self.npcs["nome_do_npc"].story = minha_historia`).

### Constantes de Configuração (`config.py`)

*   `WIDTH`, `HEIGHT`: Dimensões da janela do jogo.
*   `FPS`: Taxa de quadros por segundo.
*   `MAP_WIDTH`, `MAP_HEIGHT`: Dimensões totais do mapa do jogo em pixels. Deve corresponder à imagem `map_image.png` e ao layout de tiles.
*   Cores: Constantes de cores (ex: `BLACK`, `WHITE`, `BLUE`).

### Sistema de Câmera (`camera.py`)

*   A câmera segue o jogador.
*   Ela centraliza o jogador na tela, levando em consideração as dimensões do sprite do jogador (`map_sprite_width`, `map_sprite_height`).
*   A câmera é limitada pelas bordas do mapa (`MAP_WIDTH`, `MAP_HEIGHT`).

## Assets

*   Todos os assets (imagens, mapas de tiles) estão localizados em `src/assets/`.
*   **Sprites**: As imagens dos personagens devem ter fundo transparente (PNG é recomendado).
    *   Para animação de 2 frames, a imagem deve conter os dois frames lado a lado horizontalmente.
    *   Exemplo: Se cada frame individual tem 28x34 pixels, a imagem do sprite (ex: `sprite_knight_frente.png`) deve ter 56x34 pixels. Se a imagem carregada tiver dimensões 28x34, será tratada como um sprite de frame único.
*   **Tiles**: Imagens para os tiles do mapa. O tamanho em que são desenhados é controlado por `self.tile_size` em `game.py`.

Lembre-se de que este é um projeto em desenvolvimento e algumas funcionalidades podem ser expandidas ou modificadas.
