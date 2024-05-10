import pygame
import random
import Fish

D_PERSONALITY = 0
D_SHOW_GOAL = False
D_SHOW_PATH = False
D_BUBBLES = False

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fish Bowl Sim")

FONT = pygame.font.SysFont("Consolas", 16, True)

COLORS = {
    "background": (115, 175, 255),
    "trail": (255, 255, 255),
    "food": (255, 255, 0),
    "fish": (100, 10, 10)
}

PERSONALITY_COLORS = [
    (100, 10, 10),  # Neutral
    (80, 80, 80),  # Timid
    (80, 250, 100),  # Friendly
    (150, 30, 150)  # Bubble Chaser
]


def clear_screen():
    WINDOW.fill(COLORS["background"])


def get_random_map_point() -> tuple[int, int]:
    return random.randrange(0, WINDOW_WIDTH), random.randrange(0, WINDOW_HEIGHT)


def is_in_map_bounds(x, y) -> bool:
    return not (x <= 0 or x >= WINDOW_WIDTH or y <= 0 or y >= WINDOW_HEIGHT)


def handle_events():
    global RUNNING, fishes, D_PERSONALITY, D_BUBBLES, D_SHOW_GOAL, D_SHOW_PATH

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                RUNNING = False
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    food.append(Fish.Food(pygame.mouse.get_pos(), WINDOW_HEIGHT))
                if event.button == 3:
                    fishes.append(Fish.Fish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT),
                                            personality=D_PERSONALITY))
            case pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fishes = []
                if event.key == pygame.K_LEFT:
                    D_PERSONALITY -= 1
                if event.key == pygame.K_RIGHT:
                    D_PERSONALITY += 1
                if event.key == pygame.K_c:
                    D_BUBBLES = not D_BUBBLES
                if event.key == pygame.K_z:
                    D_SHOW_PATH = not D_SHOW_PATH
                if event.key == pygame.K_x:
                    D_SHOW_GOAL = not D_SHOW_GOAL


def create_bubbles(percent_chance: float):
    for i in range(0, WINDOW_WIDTH):
        if random.random() <= percent_chance:
            bubbles.append(Fish.Bubble((i, WINDOW_HEIGHT), random.randint(6, 30)))


RUNNING = True

food: list[Fish.Food] = []
fishes: list[Fish.Fish] = []
bubbles: list[Fish.Bubble] = []


def main():
    while RUNNING:
        handle_events()
        clear_screen()

        if D_BUBBLES:
            create_bubbles(0.00003)

        for fish in fishes:
            fish.run(fishes, food, bubbles)
            fish.draw(WINDOW, PERSONALITY_COLORS[fish.personality], FONT)
            if D_SHOW_PATH:
                fish.draw_line_to_wander_goal(WINDOW, (255, 255, 255))
            if D_SHOW_GOAL:
                fish.draw_wander_goal(WINDOW, PERSONALITY_COLORS[fish.personality])

        for pellet in food:
            pellet.fall()
            pellet.draw(WINDOW, COLORS["food"])

        for bubble in bubbles:
            bubble.rise(bubbles)
            bubble.draw(WINDOW)

        settings_rect = pygame.Rect(5, 15, WINDOW_WIDTH, 20)
        settings_label = FONT.render(
            f'| [L/R] PERSONALITY: {D_PERSONALITY} | [Z] SHOW PATH: {D_SHOW_PATH} | [X] SHOW GOAL: {D_SHOW_GOAL} | ['
            f'C] BUBBLES: {D_BUBBLES}',
            True,
            (255, 255, 255, 80), True)
        WINDOW.blit(settings_label, settings_rect)

        pygame.display.update()
        pygame.time.delay(10)


main()

pygame.quit()
