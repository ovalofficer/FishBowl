import pygame
import random
import Fish

D_PERSONALITY = 0
D_SHOW_GOAL = False
D_SHOW_PATH = False
D_BUBBLES = False
D_NAMETAG = True

FPS_CAP = 60

pygame.init()
pygame.mixer.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
OVERLAY_SURFACE = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

pygame.display.set_caption("Fish Bowl Sim")

FONT = pygame.font.SysFont("Consolas", 16, True)

timer = pygame.time.Clock()

IMAGES = {

}

COLORS = {
    "background": (115, 175, 255),
    "distant_background": (80, 140, 220),
    "trail": (255, 255, 255),
    "food": (255, 255, 0),
    "fish": (100, 10, 10)
}

PERSONALITY_COLORS = [
    (255, 150, 10),  # Neutral
    (80, 80, 80),  # Timid
    (80, 250, 100),  # Friendly
    (150, 30, 150)  # Bubble Chaser
]

personalities = {
    0: {"name": "Neutral",
        "description": "This fish has no preference for where to be. They will wander the tank aimlessly "
                       "and chase food when they are hungry."},
    1: {"name": "Timid",
        "description": "This fish prefers to stay away from the others. They will hang around the corners of the "
                       "tank and chase food only if another fish isn't going for it already."},
    2: {"name": "Friendly",
        "description": "This fish prefers to stay near the others. They will hang around the middle of the tank, "
                       "and race other fish to get food."},
    3: {"name": "Bubble Chaser",
        "description": "This fish does not wander like the rest. They only want to pop bubbles. They will eat "
                       "only when necessary. All fish actively avoid the bubble chasers -- they don't seem stable."}
}


def clear_screen():
    top_left = (WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8)
    top_right = (WINDOW_WIDTH - WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8)
    bottom_left = (WINDOW_WIDTH // 4, WINDOW_HEIGHT - WINDOW_HEIGHT // 4)
    bottom_right = (WINDOW_WIDTH - WINDOW_WIDTH // 4, WINDOW_HEIGHT - WINDOW_HEIGHT // 4)
    WINDOW.fill(COLORS["background"])
    WINDOW.blit(OVERLAY_SURFACE, (0, 0))
    OVERLAY_SURFACE.fill((0, 0, 0, 0))

    pygame.draw.rect(WINDOW, COLORS["distant_background"], (
        WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8, WINDOW_WIDTH - WINDOW_WIDTH // 4,
        WINDOW_HEIGHT - WINDOW_HEIGHT // 4))
    pygame.draw.line(OVERLAY_SURFACE, (255, 255, 255, 80), (0, 0), top_left, 4)
    pygame.draw.line(OVERLAY_SURFACE, (255, 255, 255, 80), (0, WINDOW_HEIGHT), bottom_left, 4)
    pygame.draw.line(OVERLAY_SURFACE, (255, 255, 255, 80), (WINDOW_WIDTH, 0), top_right, 4)
    pygame.draw.line(OVERLAY_SURFACE, (255, 255, 255, 80), (WINDOW_WIDTH, WINDOW_HEIGHT), bottom_right, 4)


def draw_shadow(x):
    for i in range(10):
        pygame.draw.ellipse(OVERLAY_SURFACE, (0, 0, 0, (i * 3)), (x - (50 - i * 5), WINDOW_HEIGHT - (50 - i), 100 - (i * 10), 30 - (i * 3)), 1)


def get_random_map_point() -> tuple[int, int]:
    return random.randrange(0, WINDOW_WIDTH), random.randrange(0, WINDOW_HEIGHT)


def is_in_map_bounds(x, y) -> bool:
    return not (x <= 0 or x >= WINDOW_WIDTH or y <= 0 or y >= WINDOW_HEIGHT)


def handle_events():
    global RUNNING, fishes, D_PERSONALITY, D_BUBBLES, D_SHOW_GOAL, D_SHOW_PATH, D_NAMETAG

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                RUNNING = False
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    food.append(Fish.Food(pygame.mouse.get_pos(), WINDOW_HEIGHT))
                if event.button == 3:
                    fishes.append(Fish.Fish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT - 100),
                                            personality=D_PERSONALITY))
            case pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fishes = []
                if event.key == pygame.K_LEFT:
                    D_PERSONALITY = max(D_PERSONALITY - 1, 0)
                if event.key == pygame.K_RIGHT:
                    D_PERSONALITY = min(D_PERSONALITY + 1, len(personalities) - 1)
                if event.key == pygame.K_c:
                    D_BUBBLES = not D_BUBBLES
                if event.key == pygame.K_z:
                    D_SHOW_PATH = not D_SHOW_PATH
                if event.key == pygame.K_x:
                    D_SHOW_GOAL = not D_SHOW_GOAL
                if event.key == pygame.K_v:
                    D_NAMETAG = not D_NAMETAG


def create_bubbles(percent_chance: float):
    for i in range(0, WINDOW_WIDTH):
        if random.random() <= percent_chance:
            bubbles.append(Fish.Bubble((i, WINDOW_HEIGHT), random.randint(6, 30)))


def draw_tank_overlay():
    for i in range(255):
        pygame.draw.circle(OVERLAY_SURFACE, (120, 120, 120, i), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
                           (WINDOW_WIDTH // 2) + i, 2)


RUNNING = True

food: list[Fish.Food] = []
fishes: list[Fish.Fish] = []
bubbles: list[Fish.Bubble] = []


def main():
    while RUNNING:
        timer.tick(FPS_CAP)
        handle_events()
        clear_screen()

        if D_BUBBLES:
            create_bubbles(0.00003)

        for fish in fishes:
            fish.run(fishes, food, bubbles)
            fish.draw(WINDOW)
            if D_NAMETAG:
                fish.draw_nametag(WINDOW, PERSONALITY_COLORS[fish.personality], FONT)
            if D_SHOW_PATH:
                fish.draw_line_to_wander_goal(WINDOW, (255, 255, 255))
            if D_SHOW_GOAL:
                fish.draw_wander_goal(WINDOW, PERSONALITY_COLORS[fish.personality])
            draw_shadow(fish.pos[0])

        for pellet in food:
            pellet.fall(food)
            pellet.draw(WINDOW)

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

        # draw_tank_overlay()
        pygame.display.update()
        pygame.time.delay(8)


main()

pygame.quit()
