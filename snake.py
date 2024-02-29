# Importaciones y configuraciones iniciales
import pygame
import time
import random
import numpy as np

# Función para cargar el número de ejecuciones desde un archivo
def load_runs():
    try:
        with open("runs.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0  # Si el archivo no existe, empieza desde 0
    

runs = load_runs()
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
fruit_positions = [[random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10] for _ in range(5)]  # Genera 5 frutas
fruit_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0



# Función para guardar el número de ejecuciones en un archivo
def save_runs(runs):
    with open("runs.txt", "w") as file:
        file.write(str(runs))


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

    # Calculate distances to the two closest fruits and discretize
    closest_distances = find_distances_to_fruits(game['snake_position'], game['fruit_positions'])
    closest_distances = [discretize_distance(d) for d in closest_distances]

    # Flatten the closest_distances list
    closest_distances_flat = [item for sublist in closest_distances for item in sublist]

    state = [
        # Danger indicators
        (dir_r and is_collision(point_r, game)) or (dir_l and is_collision(point_l, game)) or 
        (dir_u and is_collision(point_u, game)) or (dir_d and is_collision(point_d, game)),
        (dir_u and is_collision(point_r, game)) or (dir_d and is_collision(point_l, game)) or 
        (dir_l and is_collision(point_u, game)) or (dir_r and is_collision(point_d, game)),
        (dir_d and is_collision(point_r, game)) or (dir_u and is_collision(point_l, game)) or 
        (dir_r and is_collision(point_u, game)) or (dir_l and is_collision(point_d, game)),
        dir_l, dir_r, dir_u, dir_d,
    ] + closest_distances_flat  # Append the flattened distance indicators
    # print(state)
    return np.array(state, dtype=int)



def is_collision(point, game):
    if point[0] < 0 or point[0] > window_x-10 or point[1] < 0 or point[1] > window_y-10:
        return True
    if point in game['snake_body'][1:]:
        return True
    return False

def discretize_distance(distancia):
    # Retorna un vector binario en lugar de un valor escalar
    if distancia < 50:
        return [1, 0, 0, 0]  # Muy cerca
    elif distancia < 100:
        return [0, 1, 0, 0]  # Cerca
    elif distancia < 150:
        return [0, 0, 1, 0]  # Lejos
    else:
        return [0, 0, 0, 1]  # Muy lejos


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

def game_over(score):
    global exploration_rate, runs
    print(f'Game Over. Runs: {runs}, Score: {score}')

    np.save("q_table.npy", q_table)
    reset_game()
    exploration_rate *= 0.99

def reset_game():
    global snake_position, snake_body, fruit_positions, fruit_spawn, score, direction, runs
    runs += 1  # Incrementa el contador de partidas
    save_runs(runs)  # Guarda el número de ejecuciones actualizado en el archivo
    snake_position = [360, 240]  # Coloca la serpiente en el centro de la ventana
    snake_body = [[360, 240], [350, 240], [340, 240], [330, 240]]  # Ajusta el cuerpo acorde
    # Regenerar todas las frutas
    fruit_positions = [[random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10] for _ in range(5)]
    fruit_spawn = True
    score = 0
    direction = 'RIGHT'


def state_to_index(state):
    """Convierte un estado binario a un índice entero."""
    # Convierte el array binario a un string de dígitos y luego a un entero base 2
    return int("".join(str(int(x)) for x in state), 2)

def find_closest_fruit(snake_position, fruit_positions):
    """
    Encuentra la fruta más cercana a la posición actual de la serpiente.
    """
    closest_fruit = None
    min_distance = float('inf')
    for fruit_position in fruit_positions:
        distance = np.linalg.norm(np.array(snake_position) - np.array(fruit_position))
        if distance < min_distance:
            min_distance = distance
            closest_fruit = fruit_position
    return closest_fruit

def find_distances_to_fruits(snake_position, fruit_positions):
    """
    Calcula las distancias de la posición de la serpiente a todas las frutas y las retorna ordenadas.
    """
    distances = [np.linalg.norm(np.array(snake_position) - np.array(fruit)) for fruit in fruit_positions]
    distances.sort()
    return distances[:2]  

    
def initialize_q_table():
    global q_table  # Asegúrate de declarar q_table como global si va a ser usada fuera de esta función
    # Intenta cargar la tabla Q existente; si no existe, inicializa una nueva
    try:
        q_table = np.load("q_table.npy")
    except FileNotFoundError:
        # Usa la función get_state ahora que ya está definida
        dummy_state = get_state({'snake_position': [360, 240], 'snake_body': [[360, 240], [350, 240], [340, 240], [330, 240]], 'direction': 'RIGHT', 'fruit_positions': [random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10]})
        q_table = np.zeros((2**len(dummy_state), 3))

initialize_q_table()

# Parámetros de aprendizaje
learning_rate = 0.1
discount_factor = 0.99
exploration_rate = 1.0
max_exploration_rate = 1.0
min_exploration_rate = 0.01
exploration_decay_rate = 0.01
move_count = 0
reward=0
# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # No necesitas buscar la fruta más cercana para el estado ya que vamos a pasar todas las frutas
    # closest_fruit = find_closest_fruit(snake_position, fruit_positions)
    # fruit_position = closest_fruit
    move_count += 1
    time_based_reward_multiplier = 1 + (move_count // 100) * 0.1  # Aumenta en 0.1 por cada 100 movimientos


    # Continúa con el bucle principal del juego
    if not fruit_spawn:
        fruit_positions.append([random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10])  # Añade una nueva fruta si se necesita
        fruit_spawn = True

    # Actualizar el estado para pasar todas las posiciones de las frutas
    state = get_state({
        'snake_position': snake_position,
        'snake_body': snake_body,
        'direction': direction,
        'fruit_positions': fruit_positions  # Ahora pasamos todas las posiciones
    })

    state_index = state_to_index(state)  # Convertir el estado a un índice entero

    exploration_rate_threshold = random.uniform(0, 1)
    print(f'threshold: {exploration_rate_threshold}, exploration: {exploration_rate}')

    if exploration_rate_threshold > exploration_rate:
        action = np.argmax(q_table[state_index])  # Usar el índice entero con q_table
        print("IA decision")
    else:
        action = random.randint(0, 2)
        print("Random")


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
        game_over(score)

    # Insertar nueva posición de la cabeza y verificar si come fruta
    snake_body.insert(0, list(snake_position))
    if snake_position in fruit_positions:
        score += 10
        fruit_spawn = False
        fruit_positions.remove(snake_position)  # Remueve la fruta comida de la lista
        # Ajusta la recompensa por comer fruta basada en el tiempo
        reward = 10 * time_based_reward_multiplier
    else:
        snake_body.pop()
        # reward = -10 

    game_window.fill(black)
    for pos in snake_body:
        if pos == snake_body[0]:  # Si es la cabeza de la serpiente
            pygame.draw.rect(game_window, red, pygame.Rect(pos[0], pos[1], 10, 10))
        else:  # Para el resto del cuerpo
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    
    for fruit_pos in fruit_positions:
        pygame.draw.rect(game_window, red, pygame.Rect(fruit_pos[0], fruit_pos[1], 10, 10))
    
    show_score(1, white, 'times new roman', 20)
    pygame.display.update()
    fps.tick(snake_speed)

    new_state = get_state({
        'snake_position': snake_position,
        'snake_body': snake_body,
        'direction': direction,
        'fruit_positions': fruit_positions  # Pasamos todas las posiciones para el nuevo estado también
    })
    new_state_index = state_to_index(new_state)

    q_table[state_index, action] = q_table[state_index, action] * (1 - learning_rate) + \
        learning_rate * (reward + discount_factor * np.max(q_table[new_state_index]))

    exploration_rate = min_exploration_rate + \
        (max_exploration_rate - min_exploration_rate) * np.exp(-exploration_decay_rate * runs)

