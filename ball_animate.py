import pygame
import math
import sys


# === ЦЕНТРАЛЬНОЕ УПРАВЛЕНИЕ ПАРАМЕТРАМИ ===
class SimulationParams:
    # Окно
    WIDTH = 1000  # увеличено
    HEIGHT = 800  # увеличено
    FPS = 60

    # Цвета
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    # Шарик
    BALL_RADIUS = 20
    BALL_START_POS = [WIDTH // 2, HEIGHT // 2 - 100]
    BALL_START_VEL = [1.0, 0.0]

    # Физика
    GRAVITY = 0.1
    BOUNCE_ELASTICITY = 1
    MAX_BALL_SPEED = 30
    SUBSTEP_THRESHOLD = 15.0

    # Фигура
    INITIAL_SIDES = 3  # Треугольник
    POLYGON_CENTER = (WIDTH // 2, HEIGHT // 2)
    POLYGON_RADIUS = 350  # увеличено пропорционально
    EDGE_THICKNESS = 10  # можно уменьшить толщину, т.к. разрешение выше

    # Шрифт
    FONT_SIZE = 24
    FONT_NAME = 'Arial'


# === КОНСТАНТЫ ИЗ ПАРАМЕТРОВ ===
P = SimulationParams()

pygame.init()
screen = pygame.display.set_mode((P.WIDTH, P.HEIGHT))
pygame.display.set_caption("Прыгающий шарик")
clock = pygame.time.Clock()
font = pygame.font.SysFont(P.FONT_NAME, P.FONT_SIZE)

# Переменные симуляции
ball_pos = P.BALL_START_POS[:]
ball_vel = P.BALL_START_VEL[:]
current_sides = P.INITIAL_SIDES
bounce_count = 0


def get_polygon_points(sides, center, radius):
    """Возвращает список точек многоугольника."""
    cx, cy = center
    points = []
    for i in range(sides):
        angle_deg = 90 + i * (360 / sides)
        angle_rad = math.radians(angle_deg)
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)
        points.append((x, y))
    return points


def distance_point_to_line(px, py, x1, y1, x2, y2):
    """Расстояние от точки до отрезка (стороны)."""
    A = x2 - x1
    B = y2 - y1
    C = -(A * x1 + B * y1)
    dist = abs(A * px + B * py + C) / math.sqrt(A ** 2 + B ** 2)

    line_len_sq = A ** 2 + B ** 2
    if line_len_sq == 0:
        return math.hypot(px - x1, py - y1), px, py

    t = max(0, min(1, ((px - x1) * A + (py - y1) * B) / line_len_sq))
    proj_x = x1 + t * A
    proj_y = y1 + t * B
    return math.hypot(px - proj_x, py - proj_y), proj_x, proj_y


def reflect_velocity(vel, nx, ny, elasticity=P.BOUNCE_ELASTICITY):
    dot = vel[0] * nx + vel[1] * ny
    rx = vel[0] - 2 * dot * nx
    ry = vel[1] - 2 * dot * ny
    return [rx * elasticity, ry * elasticity]


def limit_speed(vel, max_speed=P.MAX_BALL_SPEED):
    speed = math.hypot(vel[0], vel[1])
    if speed > max_speed:
        scale = max_speed / speed
        return [vel[0] * scale, vel[1] * scale]
    return vel


running = True
while running:
    dt = clock.tick(P.FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- СУБШАГИ ---
    speed = math.hypot(ball_vel[0], ball_vel[1])
    substeps = max(1, int(speed / P.SUBSTEP_THRESHOLD))
    dt_sub = 1.0 / substeps

    for _ in range(substeps):
        ball_vel[1] += P.GRAVITY * dt_sub
        prev_pos = ball_pos[:]
        ball_pos[0] += ball_vel[0] * dt_sub
        ball_pos[1] += ball_vel[1] * dt_sub

        polygon_points = get_polygon_points(current_sides, P.POLYGON_CENTER, P.POLYGON_RADIUS)

        for i in range(len(polygon_points)):
            p1 = polygon_points[i]
            p2 = polygon_points[(i + 1) % len(polygon_points)]

            dist, proj_x, proj_y = distance_point_to_line(
                ball_pos[0], ball_pos[1], p1[0], p1[1], p2[0], p2[1]
            )

            if dist <= P.BALL_RADIUS:
                edge_x = p2[0] - p1[0]
                edge_y = p2[1] - p1[1]
                length = math.hypot(edge_x, edge_y)
                if length == 0:
                    continue
                nx = -edge_y / length
                ny = edge_x / length

                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                to_center_x = P.POLYGON_CENTER[0] - mid_x
                to_center_y = P.POLYGON_CENTER[1] - mid_y
                if (nx * to_center_x + ny * to_center_y) < 0:
                    nx, ny = -nx, -ny

                penetration = P.BALL_RADIUS - dist + 0.1
                ball_pos[0] += nx * penetration
                ball_pos[1] += ny * penetration

                ball_vel = reflect_velocity(ball_vel, nx, ny)
                ball_vel = limit_speed(ball_vel)

                bounce_count += 1
                current_sides += 1

                break

    # Рисуем всё
    screen.fill(P.WHITE)

    # Рисуем многоугольник с сглаженными линиями
    if len(polygon_points) > 2:
        pygame.draw.lines(screen, P.BLACK, True, polygon_points, P.EDGE_THICKNESS)

    # Рисуем шарик с сглаживанием
    pygame.draw.circle(screen, P.RED, (int(ball_pos[0]), int(ball_pos[1])), P.BALL_RADIUS)

    # Счётчик
    counter_text = font.render(f"Отскоков: {bounce_count}", True, P.BLACK)
    screen.blit(counter_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()