import pygame
import pygame.gfxdraw
import random
import Fish

D_PERSONALITY = 0
D_SHOW_GOAL = False
D_SHOW_PATH = False
D_BUBBLES = False
D_NAMETAG = False
D_SHADOWS = True

FPS_CAP = 60

pygame.init()
pygame.mixer.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
OVERLAY_SURFACE = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

pygame.display.set_caption("Fish Bowl Sim")

FONT = pygame.font.SysFont("Consolas", 16, True)

NAMETAG_FONT = pygame.font.SysFont("Comic Sans", 18, True)

timer = pygame.time.Clock()

IMAGES = {

    "sand": pygame.image.load('./sprites/SandFloor.png')
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
                       "only when necessary. Neutral fish actively avoid the bubble chasers -- they don't seem stable."}
}

''' WIP##############
commands = {
    "help": "Displays this help menu",
}

CONSOLE = GameConsole.Console(WINDOW, commands, personalities)
'''


def clear_screen():
    top_left = (WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8)
    top_right = (WINDOW_WIDTH - WINDOW_WIDTH // 8, WINDOW_HEIGHT // 8)
    bottom_left = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - WINDOW_HEIGHT // 2)
    bottom_right = (WINDOW_WIDTH - WINDOW_WIDTH // 2, WINDOW_HEIGHT - WINDOW_HEIGHT // 2)
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

    pygame.draw.polygon(OVERLAY_SURFACE, (0, 0, 0, 255),
                        ((0, WINDOW_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT), bottom_left, bottom_right))

    pygame.gfxdraw.textured_polygon(OVERLAY_SURFACE,
                                    ((0, WINDOW_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT), bottom_left, bottom_right),
                                    IMAGES["sand"], 0, 10)


def draw_shadow(pos):
    percent_to_floor = pos[1] / WINDOW_HEIGHT
    lightness = 255 - (150 * percent_to_floor)

    pygame.draw.ellipse(OVERLAY_SURFACE, (lightness, lightness, lightness, 255),
                        (pos[0] - 10, WINDOW_HEIGHT - 50, 50 * percent_to_floor, (30 * percent_to_floor) - 15), 20)


def get_random_map_point() -> tuple[int, int]:
    return random.randrange(0, WINDOW_WIDTH), random.randrange(0, WINDOW_HEIGHT)


def is_in_map_bounds(x, y) -> bool:
    return not (x <= 0 or x >= WINDOW_WIDTH or y <= 0 or y >= WINDOW_HEIGHT)


def handle_events():
    global RUNNING, fishes, D_PERSONALITY, D_BUBBLES, D_SHOW_GOAL, D_SHOW_PATH, D_NAMETAG, D_SHADOWS

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                RUNNING = False
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    food.append(Fish.Food(pygame.mouse.get_pos(), WINDOW_HEIGHT))
                if event.button == 3:
                    # fishes.append(Fish.Fish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT - 60),personality=D_PERSONALITY))
                    match D_PERSONALITY:
                        case 0:
                            fishes.append(
                                Fish.NeutralFish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT - 60)))
                        case 1:
                            fishes.append(
                                Fish.TimidFish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT - 60)))
                        case 2:
                            fishes.append(
                                Fish.FriendlyFish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT - 60)))
                        case 3:
                            fishes.append(
                                Fish.BubbleChaserFish(len(fishes), pygame.mouse.get_pos(), (WINDOW_WIDTH, WINDOW_HEIGHT - 60)))

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
                if event.key == pygame.K_b:
                    D_SHADOWS = not D_SHADOWS


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

        Fish.Fish.foods = food
        Fish.Fish.fishes = fishes
        Fish.Fish.bubbles = bubbles

        timer.tick(FPS_CAP)
        handle_events()
        clear_screen()

        if D_BUBBLES:
            create_bubbles(0.000015)

        for fish in fishes:
            fish.run()
            fish.draw(WINDOW)
            fish.draw_hunger_bar(WINDOW)
            if D_NAMETAG:
                fish.draw_nametag(WINDOW, PERSONALITY_COLORS[1], NAMETAG_FONT)
            if D_SHOW_PATH:
                fish.draw_line_to_wander_goal(WINDOW, (255, 255, 255))
            if D_SHOW_GOAL:
                fish.draw_wander_goal(WINDOW, PERSONALITY_COLORS[1])
            if D_SHADOWS:
                draw_shadow(fish.pos)

        for pellet in food:
            pellet.fall(food)
            pellet.draw(WINDOW)

        for bubble in bubbles:
            bubble.rise(bubbles)
            bubble.draw(WINDOW)

        settings_rect = pygame.Rect(5, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 20)
        settings_label = FONT.render(
            f'[L/R] PERSONALITY: {personalities[D_PERSONALITY]["name"]} | [Z] SHOW PATH: {D_SHOW_PATH} | [X] SHOW GOAL: {D_SHOW_GOAL} |'
            f'[C] BUBBLES: {D_BUBBLES} | [V] NAMETAGS: {D_NAMETAG} | [B] SHADOWS: {D_SHADOWS}',
            True,
            (255, 255, 255, 80), True)
        WINDOW.blit(settings_label, settings_rect)

        fps_label = FONT.render(f'FPS: {str(int(timer.get_fps()))}', False,
                                (255 - timer.get_fps(), timer.get_fps() * 4, 0), True)
        WINDOW.blit(fps_label, (5, 5, 15, 15))
        # draw_tank_overlay()
        pygame.display.update()
        pygame.time.delay(8)


main()

pygame.quit()
