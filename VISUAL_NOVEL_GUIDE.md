# Visual Novel - Guia de Desenvolvimento

## Como Jogar
- **ESPAÇO**: Avançar na história
- **ESC**: Sair do jogo

## Estrutura do Projeto

### `game.py`
Contém toda a lógica da visual novel:

#### Classes Principais:
- **Character**: Representa um personagem da história
- **DialogueSystem**: Sistema de diálogos e caixas de texto
- **Story**: Gerencia as cenas e progressão da história
- **Game**: Classe principal que coordena tudo

## Como Expandir Sua História

### 1. Adicionando Novos Personagens
```python
# Em Game.__init__()
self.characters = {
    "protagonist": Character("Protagonista", BLUE),
    "amigo": Character("Amigo", (255, 100, 100)),  # Vermelho
    "villao": Character("Vilão", (100, 100, 100))  # Cinza
}
```

### 2. Adicionando Novas Cenas
Edite a lista `scenes` na classe `Story`:
```python
self.scenes = [
    {
        "background": "floresta",
        "character": "protagonist", 
        "text": "Seu texto aqui..."
    },
    # Adicione mais cenas...
]
```

### 3. Adicionando Novos Backgrounds
Na função `draw_background()`, adicione novos cenários:
```python
elif background_name == "cidade":
    # Desenhe uma cidade
    pygame.draw.rect(self.screen, (169, 169, 169), (0, 0, WIDTH, HEIGHT))
    # Adicione prédios, etc...
```

### 4. Substituindo Placeholders por Pixel Art

#### Para Personagens:
1. Coloque suas imagens na pasta `src/assets/characters/`
2. Modifique a classe `Character`:
```python
def __init__(self, name, sprite_path=None):
    self.name = name
    if sprite_path:
        self.sprite = pygame.image.load(sprite_path)
    else:
        self.sprite = None
```

#### Para Backgrounds:
1. Coloque suas imagens na pasta `src/assets/backgrounds/`
2. Modifique a função `draw_background()`:
```python
def draw_background(self, background_name):
    try:
        bg_image = pygame.image.load(f"src/assets/backgrounds/{background_name}.png")
        self.screen.blit(bg_image, (0, 0))
    except:
        # Fallback para placeholder
        self.draw_placeholder_background(background_name)
```

## Adicionando Recursos Avançados

### 1. Sistema de Escolhas
```python
# Adicione à classe Story
"choices": [
    {"text": "Ir para a floresta", "next_scene": 5},
    {"text": "Ir para a cidade", "next_scene": 10}
]
```

### 2. Sistema de Inventário
```python
# Adicione à classe Game
self.inventory = []

def add_item(self, item):
    self.inventory.append(item)
```

### 3. Mini-Puzzles
```python
# Adicione cenas especiais com tipo "puzzle"
{
    "type": "puzzle",
    "puzzle_type": "math",
    "question": "Quanto é 2 + 2?",
    "answer": "4"
}
```

### 4. Sistema de Save/Load
```python
import json

def save_game(self, filename="save.json"):
    save_data = {
        "current_scene": self.story.current_scene,
        "inventory": self.inventory
    }
    with open(filename, 'w') as f:
        json.dump(save_data, f)
```

## Estrutura de Arquivos Recomendada
```
src/
├── assets/
│   ├── characters/
│   │   ├── protagonist.png
│   │   └── amigo.png
│   ├── backgrounds/
│   │   ├── floresta.png
│   │   └── cidade.png
│   ├── ui/
│   │   └── dialogue_box.png
│   └── sounds/
│       ├── music/
│       └── sfx/
├── game.py
└── main.py
```

## Próximos Passos
1. **Crie sua história**: Escreva o roteiro e adicione mais cenas
2. **Pixel Art**: Substitua os placeholders por suas artes
3. **Som**: Adicione música e efeitos sonoros
4. **Interatividade**: Implemente escolhas e puzzles
5. **Polish**: Adicione transições, animações e efeitos especiais

Boa sorte com sua visual novel! 🎮✨
