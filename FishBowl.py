import pygame
import random
import Fish

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


def clear_screen():
    WINDOW.fill(COLORS["background"])


def get_random_map_point() -> tuple[int, int]:
    return random.randrange(0, WINDOW_WIDTH), random.randrange(0, WINDOW_HEIGHT)


def is_in_map_bounds(x, y) -> bool:
    return not (x <= 0 or x >= WINDOW_WIDTH or y <= 0 or y >= WINDOW_HEIGHT)


def handle_events():
    global RUNNING, fishes

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                RUNNING = False
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    food.append(Fish.Food(pygame.mouse.get_pos(), WINDOW_HEIGHT))
                if event.button == 3:
                    fishes.append(Fish.Fish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT)))
            case pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fishes = []


RUNNING = True

food: list[Fish.Food] = []
fishes: list[Fish.Fish] = []


def main():
    while RUNNING:
        handle_events()
        clear_screen()

        for fish in fishes:
            fish.run(food)
            fish.draw(WINDOW, COLORS["fish"], FONT, food)

        for pellet in food:
            pellet.fall()
            pellet.draw(WINDOW, COLORS["food"])

        pygame.display.update()
        pygame.time.delay(10)


main()

pygame.quit()
