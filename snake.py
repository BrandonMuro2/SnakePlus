# Importaciones y configuraciones iniciales
import pygame
import time
import random
import numpy as np

snake_speed = 15
window_x = 720
window_y = 480
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

pygame.init()
pygame.display.set_caption('Snake++')
game_window = pygame.display.set_mode((window_x, window_y))
fps = pygame.time.Clock()

snake_position = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50], [70, 50]]
fruit_position = [random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10]
fruit_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0

# Definiciones de funciones
def get_state(game):
    head = game['snake_position']
    point_l = [head[0] - 10, head[1]]
    point_r = [head[0] + 10, head[1]]
    point_u = [head[0], head[1] - 10]
    point_d = [head[0], head[1] + 10]

    dir_l = game['direction'] == 'LEFT'
    dir_r = game['direction'] == 'RIGHT'
    dir_u = game['direction'] == 'UP'
    dir_d = game['direction'] == 'DOWN'

    state = [
        (dir_r and is_collision(point_r, game)) or (dir_l and is_collision(point_l, game)) or 
        (dir_u and is_collision(point_u, game)) or (dir_d and is_collision(point_d, game)),
        (dir_u and is_collision(point_r, game)) or (dir_d and is_collision(point_l, game)) or 
        (dir_l and is_collision(point_u, game)) or (dir_r and is_collision(point_d, game)),
        (dir_d and is_collision(point_r, game)) or (dir_u and is_collision(point_l, game)) or 
        (dir_r and is_collision(point_u, game)) or (dir_l and is_collision(point_d, game)),
        dir_l, dir_r, dir_u, dir_d,
        game['fruit_position'][0] < game['snake_position'][0],  # Food left
        game['fruit_position'][0] > game['snake_position'][0],  # Food right
        game['fruit_position'][1] < game['snake_position'][1],  # Food up
        game['fruit_position'][1] > game['snake_position'][1]   # Food down
    ]

    return np.array(state, dtype=int)

def is_collision(point, game):
    if point[0] < 0 or point[0] > window_x-10 or point[1] < 0 or point[1] > window_y-10:
        return True
    if point in game['snake_body'][1:]:
        return True
    return False

def update_direction(current_direction, action):
    directions = ['UP', 'RIGHT', 'DOWN', 'LEFT']
    idx = directions.index(current_direction)

    if action == 0:  # Girar a la izquierda
        new_dir = directions[(idx - 1) % 4]
    elif action == 1:  # Seguir recto
        new_dir = current_direction
    elif action == 2:  # Girar a la derecha
        new_dir = directions[(idx + 1) % 4]

    return new_dir

def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    game_window.blit(score_surface, score_rect)

def game_over():
    print('game over' )
    global exploration_rate

    np.save("q_table.npy", q_table)
    # Mostrar algún mensaje de Game Over si lo deseas
    reset_game()
    # También podrías querer reducir la tasa de exploración aquí si usas un enfoque de decaimiento
    exploration_rate *= 0.99  # Solo un ejemplo, ajusta según sea necesario

def reset_game():
    global snake_position, snake_body, fruit_position, fruit_spawn, score, direction
    snake_position = [360, 240]  # Coloca la serpiente en el centro de la ventana
    snake_body = [[360, 240], [350, 240], [340, 240], [330, 240]]  # Ajusta el cuerpo acorde
    fruit_position = [random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10]
    fruit_spawn = True
    score = 0
    direction = 'RIGHT'


def state_to_index(state):
    """Convierte un estado binario a un índice entero."""
    # Convierte el array binario a un string de dígitos y luego a un entero base 2
    return int("".join(str(int(x)) for x in state), 2)
    
def initialize_q_table():
    global q_table  # Asegúrate de declarar q_table como global si va a ser usada fuera de esta función
    # Intenta cargar la tabla Q existente; si no existe, inicializa una nueva
    try:
        q_table = np.load("q_table.npy")
    except FileNotFoundError:
        # Usa la función get_state ahora que ya está definida
        dummy_state = get_state({'snake_position': [360, 240], 'snake_body': [[360, 240], [350, 240], [340, 240], [330, 240]], 'direction': 'RIGHT', 'fruit_position': [random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10]})
        q_table = np.zeros((2**len(dummy_state), 3))

initialize_q_table()

# Parámetros de aprendizaje
learning_rate = 0.1
discount_factor = 0.99
exploration_rate = 5.0
max_exploration_rate = 1.0
min_exploration_rate = 0.01
exploration_decay_rate = 0.01

# Bucle principal del juego
# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    state = get_state({
        'snake_position': snake_position,
        'snake_body': snake_body,
        'direction': direction,
        'fruit_position': fruit_position
    })

    state_index = state_to_index(state)  # Convertir el estado a un índice entero

    exploration_rate_threshold = random.uniform(0, 1)
    if exploration_rate_threshold > exploration_rate:
        action = np.argmax(q_table[state_index])  # Usar el índice entero con q_table
    else:
        action = random.randint(0, 2)

    # Actualizar la dirección basada en la acción
    direction = update_direction(direction, action)

    # Mover la serpiente basado en la dirección actualizada
    # Actualización de la posición de la serpiente
    if direction == 'UP':
        snake_position[1] -= 10
    elif direction == 'DOWN':
        snake_position[1] += 10
    elif direction == 'LEFT':
        snake_position[0] -= 10
    elif direction == 'RIGHT':
        snake_position[0] += 10

    # Verificar colisiones con las paredes o consigo misma
    if snake_position[0] < 0 or snake_position[0] > window_x-10 or snake_position[1] < 0 or snake_position[1] > window_y-10 or snake_position in snake_body[1:]:
        game_over()

    # Insertar nueva posición de la cabeza y verificar si come fruta
    snake_body.insert(0, list(snake_position))
    if snake_position == fruit_position:
        score += 10
        fruit_spawn = False
    else:
        snake_body.pop()

    if not fruit_spawn:
        fruit_position = [random.randrange(1, (window_x // 10)) * 10, random.randrange(1, (window_y // 10)) * 10]
    fruit_spawn = True

    game_window.fill(black)
    for pos in snake_body:
        if pos == snake_body[0]:  # Si es la cabeza de la serpiente
            pygame.draw.rect(game_window, red, pygame.Rect(pos[0], pos[1], 10, 10))
        else:  # Para el resto del cuerpo
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

    show_score(1, white, 'times new roman', 20)
    pygame.display.update()
    fps.tick(snake_speed)

    new_state = get_state({
        'snake_position': snake_position,
        'snake_body': snake_body,
        'direction': direction,
        'fruit_position': fruit_position
    })
    new_state_index = state_to_index(new_state)
    reward = 10 if snake_position == fruit_position else -10

    q_table[state_index, action] = q_table[state_index, action] * (1 - learning_rate) + \
        learning_rate * (reward + discount_factor * np.max(q_table[new_state_index]))

    exploration_rate = min_exploration_rate + \
        (max_exploration_rate - min_exploration_rate) * np.exp(-exploration_decay_rate)

