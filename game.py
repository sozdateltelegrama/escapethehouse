import pygame
import sys
import math
import random

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape the House")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
LIGHT_BROWN = (210, 180, 140)
YELLOW = (255, 255, 0)
LIGHT_YELLOW = (255, 255, 224)
DARK_BROWN = (101, 67, 33)
GRAY = (128, 128, 128)

# Дополнительные цвета для кирпичного пола
FIREBRICK = (178, 34, 34)
MORTAR = (220, 220, 220)

# Шрифт
font = pygame.font.Font(None, 36)

# Параметры игрока (Марио)
player_width = 20
player_height = 40
player_x = WIDTH // 2 - player_width // 2

# Первый этаж (пол)
floor_height = 50
floor_y = HEIGHT - floor_height  # 550
first_floor_top = floor_y - player_height  # 510
player_y_ground = first_floor_top
player_y = player_y_ground
player_speed = 5

# Гравитация и прыжок
gravity = 0.5
vertical_velocity = 0
jump_speed = -10  # отрицательное значение для прыжка

# Флаг этажа (для лестницы)
on_second_floor = False

# Второй этаж
second_floor_y = 300  # линия второго этажа
second_floor_top = (second_floor_y - floor_height) - player_height  # (300-50)-40 = 210

# Лестница
stair_width = 40
stair_x = 400
stairs_top = second_floor_top  # верхняя граница лестницы (2 этаж)
stairs_bottom_move = first_floor_top  # нижняя граница (1 этаж)
stairs_draw_bottom = floor_y  # для отрисовки лестницы до пола
stair_draw_height = stairs_draw_bottom - stairs_top  # 550 - 210 = 340

# Шкаф
wardrobe_size = 100
wardrobe_x = 100
wardrobe_y = HEIGHT - wardrobe_size - 50
wardrobe_open = False
password_entered_correctly = False

# Дверь
door_width = 80
door_height = 120
door_x = WIDTH - door_width - 50
door_y = HEIGHT - door_height - 50
door_open = False

# Лампочка
lamp_radius = 30
lamp_x = WIDTH // 2
lamp_y = 50

# Случайный пароль от шкафа (три цифры)
wardrobe_password = str(random.randint(100, 999))
input_password = ""
password_window_open = False

# Листочек с паролем на втором этаже
note_width = 30
note_height = 40
note_x = 500
note_y = second_floor_y - 100
note_window_open = False

# Ключ от двери – появляется, когда шкаф открыт
key_found = False

# Новый флаг: получен ли код (при взаимодействии с листочком)
code_received = False

# Номер комнаты (начинается с 1; NPC появляется со 2-й комнаты, а в 3-й комнате его нет)
room_number = 1

# Переменная для хранения времени начала урока по прыжкам в 3-й комнате
tutorial_start_time = None

# NPC (человек на втором этаже) – располагаем его в левой части (для 2-й комнаты)
npc_width = 20
npc_height = 40
npc_x = 50  # NPC в левой части
npc_y = second_floor_top  # фиксированная вертикальная позиция (210)
npc_chasing = False  # флаг преследования
npc_cycle_start = pygame.time.get_ticks()  # начало цикла для эффекта поворота головы
npc_turning = False  # флаг, когда NPC "оглядывается"

# Флаг завершения игры
game_over = False


def load_new_room():
    """Переход в новую комнату: сбрасываем позицию игрока, генерируем новый пароль,
    сбрасываем состояния шкафа, ключа, NPC и увеличиваем номер комнаты."""
    global player_x, player_y, wardrobe_password, wardrobe_open, key_found
    global password_entered_correctly, door_open, input_password, note_window_open, password_window_open
    global room_number, npc_x, npc_y, npc_chasing, npc_cycle_start, code_received, tutorial_start_time
    room_number += 1
    player_x = WIDTH // 2 - player_width // 2
    player_y = player_y_ground
    wardrobe_password = str(random.randint(100, 999))
    wardrobe_open = False
    key_found = False
    password_entered_correctly = False
    door_open = False
    input_password = ""
    note_window_open = False
    password_window_open = False
    code_received = False
    # Если перешли в 3-ю комнату, задаём время старта урока по прыжкам
    if room_number == 3:
        tutorial_start_time = pygame.time.get_ticks()
    else:
        tutorial_start_time = None
    # Сброс состояния NPC – для 2-й комнаты NPC остаётся, для 3-й его не будет
    npc_x = 50
    npc_y = second_floor_top
    npc_chasing = False
    npc_cycle_start = pygame.time.get_ticks()


def draw_brick_floor(x, y, width, height):
    brick_w = 50
    brick_h = 25
    pygame.draw.rect(screen, MORTAR, (x, y, width, height))
    rows = height // brick_h + 1
    cols = width // brick_w + 2
    for row in range(rows):
        offset = brick_w // 2 if row % 2 == 1 else 0
        for col in range(cols):
            brick_x = x + col * brick_w - offset
            brick_y = y + row * brick_h
            if brick_y + brick_h <= y + height + 1 and brick_x < x + width:
                pygame.draw.rect(screen, FIREBRICK, (brick_x, brick_y, brick_w, brick_h))


def draw_mario(x, y):
    # Тело (комбинезон)
    body_rect = pygame.Rect(x, y, player_width, player_height)
    pygame.draw.rect(screen, BLUE, body_rect)
    # Пуговицы
    button_radius = 2
    pygame.draw.circle(screen, WHITE, (x + player_width // 4, y + player_height // 3), button_radius)
    pygame.draw.circle(screen, WHITE, (x + 3 * player_width // 4, y + player_height // 3), button_radius)
    # Голова (прилипшая к телу)
    head_radius = 10
    head_center = (x + player_width // 2, y - head_radius)
    face_color = (255, 220, 177)
    pygame.draw.circle(screen, face_color, head_center, head_radius)
    # Кепка
    cap_rect = pygame.Rect(x - 5, head_center[1] - head_radius - 8, player_width + 10, 16)
    pygame.draw.ellipse(screen, RED, cap_rect)
    pygame.draw.ellipse(screen, RED, cap_rect, 2)
    # Глаза
    eye_radius = 2
    left_eye_center = (head_center[0] - 4, head_center[1] - 2)
    right_eye_center = (head_center[0] + 4, head_center[1] - 2)
    pygame.draw.circle(screen, BLACK, left_eye_center, eye_radius)
    pygame.draw.circle(screen, BLACK, right_eye_center, eye_radius)
    # Нос
    pygame.draw.circle(screen, BLACK, (head_center[0], head_center[1] + 1), 2)
    # Улыбка
    smile_rect = pygame.Rect(head_center[0] - 6, head_center[1], 12, 8)
    pygame.draw.arc(screen, BLACK, smile_rect, math.radians(200), math.radians(340), 2)
    # Руки
    arm_width = 5
    arm_height = player_height // 2
    pygame.draw.rect(screen, RED, (x - arm_width, y + 10, arm_width, arm_height))
    pygame.draw.rect(screen, RED, (x + player_width, y + 10, arm_width, arm_height))
    # Ноги
    leg_width = player_width // 2
    leg_height = player_height // 2
    pygame.draw.rect(screen, BLUE, (x, y + player_height, leg_width, leg_height))
    pygame.draw.rect(screen, BLUE, (x + leg_width, y + player_height, leg_width, leg_height))


def draw_light():
    light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for alpha in range(255, 0, -10):
        pygame.draw.circle(light_surface, (255, 255, 224, alpha), (lamp_x, lamp_y), lamp_radius + (255 - alpha) // 10)
    screen.blit(light_surface, (0, 0))


def draw_door(x, y, open_flag):
    pygame.draw.rect(screen, DARK_BROWN, (x, y, door_width, door_height))
    pygame.draw.circle(screen, YELLOW, (x + door_width - 10, y + door_height // 2), 5)
    if open_flag:
        pygame.draw.line(screen, DARK_BROWN, (x + door_width // 2, y), (x + door_width // 2, y + door_height), 5)


def draw_stairs(x, y, height):
    pygame.draw.rect(screen, GRAY, (x, y, stair_width, height))
    for i in range(0, height, 20):
        pygame.draw.rect(screen, DARK_BROWN, (x, y + i, stair_width, 10))


def draw_password_window():
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100))
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100), 2)
    text = font.render("Enter Password:", True, BLACK)
    screen.blit(text, (WIDTH // 2 - 140, HEIGHT // 2 - 40))
    password_text = font.render(input_password, True, BLACK)
    screen.blit(password_text, (WIDTH // 2 - 140, HEIGHT // 2))


def draw_note_window():
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100))
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100), 2)
    text = font.render("Password:", True, BLACK)
    screen.blit(text, (WIDTH // 2 - 140, HEIGHT // 2 - 40))
    password_text = font.render(wardrobe_password, True, BLACK)
    screen.blit(password_text, (WIDTH // 2 - 140, HEIGHT // 2))


def draw_npc():
    """
    Отрисовка NPC на втором этаже.
    В комнатах, отличных от 3-й, NPC с телевизором отрисовывается.
    Здесь телевизор повешен на левую стену, горизонтально и поднят выше.
    Глаза NPC становятся красными, если код получен (code_received True).
    Если NPC преследует игрока, над ним выводится надпись "RUN!".
    """
    # Отрисовка телевизора (только для комнат, где NPC есть)
    tv_fixed_x = 5
    tv_fixed_y = second_floor_top - 20  # подняли телевизор выше
    tv_rect = pygame.Rect(tv_fixed_x, tv_fixed_y, 60, 40)
    pygame.draw.rect(screen, BLACK, tv_rect)
    pygame.draw.rect(screen, WHITE, tv_rect, 2)

    # Отрисовка кресла NPC
    chair_rect = pygame.Rect(npc_x - 10, npc_y + npc_height - 10, npc_width + 20, 10)
    pygame.draw.rect(screen, DARK_BROWN, chair_rect)

    # Отрисовка тела NPC
    body_rect = pygame.Rect(npc_x, npc_y, npc_width, npc_height)
    pygame.draw.rect(screen, GREEN, body_rect)

    # Отрисовка головы NPC
    head_radius = 10
    head_center = (npc_x + npc_width // 2, npc_y - head_radius)
    face_color = (255, 220, 177)
    pygame.draw.circle(screen, face_color, head_center, head_radius)

    # Глаза: становятся красными, если code_received True
    eye_color = RED if code_received else BLACK
    eye_radius = 2
    left_eye_center = (head_center[0] - 4, head_center[1] - 2)
    right_eye_center = (head_center[0] + 4, head_center[1] - 2)
    pygame.draw.circle(screen, eye_color, left_eye_center, eye_radius)
    pygame.draw.circle(screen, eye_color, right_eye_center, eye_radius)

    # Если NPC преследует игрока, выводим надпись "RUN!"
    if npc_chasing:
        run_text = font.render("RUN!", True, RED)
        screen.blit(run_text, (npc_x, npc_y - 30))

    # Руки NPC
    pygame.draw.line(screen, GREEN, (npc_x, npc_y + 20), (npc_x - 10, npc_y + 20), 4)
    pygame.draw.line(screen, GREEN, (npc_x + npc_width, npc_y + 20), (npc_x + npc_width + 10, npc_y + 20), 4)


# Флаг для обработки нажатия клавиши E (чтобы не переключать состояние каждый кадр)
toggle_e_pressed = False

clock = pygame.time.Clock()

while not game_over:
    screen.fill(LIGHT_BROWN)
    toggle_e_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                toggle_e_pressed = True

            if event.key == pygame.K_SPACE and room_number == 3:
                # Если игрок на 3-й комнате и на полу, разрешаем прыжок
                # Проверяем: если игрок на первом этаже или на верхнем этаже (точное положение)
                if (not on_second_floor and player_y == floor_y - player_height) or (
                        on_second_floor and player_y == (second_floor_y - floor_height) - player_height):
                    vertical_velocity = jump_speed

            if password_window_open:
                if event.key == pygame.K_RETURN:
                    if input_password == wardrobe_password:
                        password_entered_correctly = True
                        wardrobe_open = True
                        key_found = True
                    input_password = ""
                    password_window_open = False
                elif event.key == pygame.K_BACKSPACE:
                    input_password = input_password[:-1]
                else:
                    if len(input_password) < 3 and event.unicode.isdigit():
                        input_password += event.unicode

            if note_window_open:
                if event.key == pygame.K_e:
                    note_window_open = False
                    # После нажатия на листочек получаем код
                    code_received = True

    keys = pygame.key.get_pressed()

    # Движение игрока по горизонтали
    if keys[pygame.K_a] and player_x > 20:
        player_x -= player_speed
    if keys[pygame.K_d] and player_x < WIDTH - player_width - 20:
        player_x += player_speed

    # Обработка лестницы
    in_stairs_region = (player_x + player_width / 2 >= stair_x and
                        player_x + player_width / 2 <= stair_x + stair_width)
    if in_stairs_region:
        vertical_velocity = 0
        if keys[pygame.K_w] and player_y > stairs_top:
            player_y -= player_speed
        if keys[pygame.K_s] and player_y < stairs_bottom_move:
            player_y += player_speed
        on_second_floor = (player_y < (stairs_top + stairs_bottom_move) / 2)
    else:
        vertical_velocity += gravity
        player_y += vertical_velocity
        if player_y + player_height > floor_y and not on_second_floor:
            player_y = floor_y - player_height
            vertical_velocity = 0
        if on_second_floor and player_y + player_height > (second_floor_y - floor_height):
            player_y = (second_floor_y - floor_height) - player_height
            vertical_velocity = 0

    # Взаимодействие с листочком
    if (player_x < note_x + note_width and
            player_x + player_width > note_x and
            player_y < note_y + note_height and
            player_y + player_height > note_y):
        if toggle_e_pressed:
            note_window_open = not note_window_open
            code_received = True

    # Взаимодействие со шкафом
    if (player_x < wardrobe_x + wardrobe_size and
            player_x + player_width > wardrobe_x and
            player_y < wardrobe_y + wardrobe_size and
            player_y + player_height > wardrobe_y):
        if toggle_e_pressed:
            if password_entered_correctly:
                wardrobe_open = not wardrobe_open
            else:
                password_window_open = True

    # Взаимодействие с дверью
    if (player_x < door_x + door_width and
            player_x + player_width > door_x and
            player_y < door_y + door_height and
            player_y + player_height > door_y):
        if toggle_e_pressed and key_found:
            door_open = not door_open
            if door_open:
                load_new_room()

    # Обработка NPC: NPC обрабатывается только в комнатах, отличных от 3-й
    if room_number >= 2 and room_number != 3:
        current_time = pygame.time.get_ticks()
        cycle_phase = (current_time - npc_cycle_start) % 7000
        if cycle_phase < 2000:
            npc_turning = True
        else:
            npc_turning = False

        npc_speed = 2
        # Если мы на втором этаже и код получен, NPC всегда преследует игрока
        if on_second_floor and code_received:
            npc_chasing = True
        else:
            if player_y < first_floor_top and not in_stairs_region and cycle_phase >= 2000:
                npc_chasing = True
            else:
                npc_chasing = False

        if npc_chasing:
            if npc_x < player_x:
                npc_x += npc_speed
            elif npc_x > player_x:
                npc_x -= npc_speed
            if abs(npc_x - player_x) < 10:
                game_over = True
        else:
            if npc_x < 50:
                npc_x += npc_speed
            elif npc_x > 50:
                npc_x -= npc_speed
            npc_y = second_floor_top

    # Отрисовка окружения
    pygame.draw.rect(screen, LIGHT_BROWN, (0, 0, WIDTH, 20))  # Верхняя стена
    pygame.draw.rect(screen, LIGHT_BROWN, (0, 0, 20, HEIGHT))  # Левая стена
    pygame.draw.rect(screen, LIGHT_BROWN, (WIDTH - 20, 0, 20, HEIGHT))  # Правая стена
    draw_brick_floor(0, floor_y, WIDTH, floor_height)
    pygame.draw.rect(screen, BROWN, (0, second_floor_y - floor_height, WIDTH, floor_height))
    draw_light()
    pygame.draw.circle(screen, YELLOW, (lamp_x, lamp_y), lamp_radius)
    pygame.draw.rect(screen, WHITE, (note_x, note_y, note_width, note_height))
    pygame.draw.rect(screen, BLACK, (note_x, note_y, note_width, note_height), 2)

    if wardrobe_open:
        pygame.draw.rect(screen, BROWN, (wardrobe_x, wardrobe_y, wardrobe_size // 2, wardrobe_size))
        pygame.draw.rect(screen, BROWN,
                         (wardrobe_x + wardrobe_size // 2, wardrobe_y, wardrobe_size // 2, wardrobe_size))
        pygame.draw.line(screen, DARK_BROWN, (wardrobe_x + wardrobe_size // 2, wardrobe_y),
                         (wardrobe_x + wardrobe_size // 2, wardrobe_y + wardrobe_size), 5)
        text = font.render("Key Found!", True, GREEN)
        screen.blit(text, (wardrobe_x, wardrobe_y - 30))
    else:
        pygame.draw.rect(screen, BROWN, (wardrobe_x, wardrobe_y, wardrobe_size, wardrobe_size))

    draw_door(door_x, door_y, door_open)
    if door_open:
        text = font.render("You Escaped!", True, GREEN)
        screen.blit(text, (door_x, door_y - 30))

    draw_stairs(stair_x, stairs_top, stair_draw_height)

    # Если комната не 3-я, отрисовываем NPC (в 3-й комнате NPC отсутствует)
    if room_number >= 2 and room_number != 3:
        draw_npc()

    draw_mario(player_x, player_y)

    if password_window_open:
        draw_password_window()
    if note_window_open:
        draw_note_window()

    # В 3-й комнате выводим текст-урок о прыжке в течение 4 секунд
    if room_number == 3 and tutorial_start_time is not None:
        current_time = pygame.time.get_ticks()
        if current_time - tutorial_start_time < 4000:
            tutorial_text = font.render("в этой комнате ты можешь прыгать", True, RED)
            screen.blit(tutorial_text, (WIDTH // 2 - 200, 50))

    pygame.display.flip()
    clock.tick(60)

screen.fill(BLACK)
game_over_text = font.render("Game Over", True, RED)
screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
sys.exit()
