import random
from typing import Self
import pygame

pygame.mixer.init()

IMAGES = {
    "food": pygame.image.load('./sprites/Food.png')

}

FISH_IMAGES: dict = {
    0: pygame.image.load('./sprites/NeutralFish.png'),

    1: pygame.image.load('./sprites/LonerFish.png'),

    2: pygame.image.load('./sprites/FriendlyFish.png'),

    3: pygame.image.load('./sprites/BubbleFish.png')
}

SOUNDS: dict = {
    "bubble_pop": pygame.mixer.Sound("./sounds/bubble-pop.mp3"),
    "fish_eat": pygame.mixer.Sound("./sounds/nom.wav"),
    "death": pygame.mixer.Sound("./sounds/death.wav")
}

for sound in SOUNDS.values():
    sound.set_volume(0.3)


class Bubble:
    shines = {
        0: [True, False, False, False],
        1: [False, True, False, False],
        2: [False, False, True, False],
        3: [False, False, False, True]

    }

    def __init__(self, pos: tuple[int, int] = (0, 0), radius: int = 12):
        self.pos = pos
        self.radius = radius
        self.shine = random.randint(0, 3)
        self.shine_amount = random.randint(1, self.radius // 10 + 1)

    def pop(self, bubbles):
        SOUNDS.get("bubble_pop").play()
        bubbles.remove(self)

    def rise(self, bubbles):
        if self.pos[1] + 8 < 0 or random.randint(0, 1500) == 1:
            self.pop(bubbles)
        else:
            self.pos = (self.pos[0] + random.randint(-1, 1), self.pos[1] - 1)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255, 80), self.pos, self.radius, 1)
        pygame.draw.circle(screen, (255, 255, 255, 80), self.pos, self.radius - self.shine_amount, self.shine_amount,
                           draw_top_left=self.shines[self.shine][0], draw_top_right=self.shines[self.shine][1],
                           draw_bottom_left=self.shines[self.shine][2], draw_bottom_right=self.shines[self.shine][3])


class Food:

    def __init__(self, pos: tuple[int, int] = (0, 0), y_limit: int = 0, nutrition: int = 1800):
        self.pos = pos
        self.floor = y_limit
        self.nutrition = nutrition

    def fall(self, foods):
        if self.pos[1] + 50 < self.floor:
            self.pos = (self.pos[0] + random.randint(-1, 1), self.pos[1] + 1)
        else:
            foods.remove(self)

    def draw(self, screen):
        pygame.draw.rect(screen, (90, 80, 45), (*self.pos, 8, 8))
        # screen.blit(pygame.transform.scale(IMAGES.get("food"), (10, 10)), self.pos)


class Fish:
    foods: list[Food]
    fishes: list[Self]
    bubbles: list[Bubble]

    def __init__(self, name, pos: tuple[int, int] = (0, 0), bounds: tuple[int, int] = (100, 100),
                 max_hunger: int = 2500,
                 max_bubble_hunger: int = 400):
        self.name = name
        self.pos = pos
        self.max_hunger = max_hunger
        self.hunger = self.max_hunger
        self.bounds = bounds
        self.closest_food = None
        self.closest_fish = self
        self.facing_left = False
        self.wander_goal: tuple = (0, 0)
        self.assign_new_wander_goal()

        # if self.personality == 3:
        #     self.max_bubble_hunger = max_bubble_hunger
        #     self.bubble_hunger = self.max_bubble_hunger

    def return_self(self) -> Self:
        return self

    def move(self, amount_x: int = 0, amount_y: int = 0):
        self.facing_left = amount_x <= 0
        self.pos = (self.pos[0] + amount_x, self.pos[1] + amount_y)

    def eat(self):
        self.hunger = min(self.hunger + self.closest_food.nutrition, self.max_hunger)

    def die(self):
        SOUNDS.get("death").play()
        Fish.fishes.remove(self)

    def increase_hunger(self):
        self.hunger = max(self.hunger - 1, 0)
        if self.hunger == 0:
            self.die()
        # if self.personality == 3:
        #     self.bubble_hunger = max(self.bubble_hunger - 1, 0)

    def is_hungry(self):
        # if self.personality == 3:
        #     return self.hunger <= 300
        # else:
        return self.hunger <= 850

    def is_within(self, pos) -> bool:
        return not (pos[0] <= 0 or pos[0] >= self.bounds[0] or pos[1] <= 0 or pos[1] >=
                    self.bounds[1])

    def get_random_map_point(self):
        return random.randint(0, self.bounds[0]), random.randint(0, self.bounds[1])

    def assign_new_wander_goal(self) -> None:
        self.wander_goal = self.get_random_map_point()

        # if self.personality == 1:  # Timid
        #     center = (self.bounds[0] // 2, self.bounds[1] // 2)
        #     while self.get_distance_to_point(self.wander_goal, center) < 500:
        #         self.wander_goal = self.get_random_map_point()
        # elif self.personality == 2:  # Friendly
        #     center = (self.bounds[0] // 2, self.bounds[1] // 2)
        #     while self.get_distance_to_point(self.wander_goal, center) > 200:
        #         self.wander_goal = self.get_random_map_point()

    def get_distance_to_point(self, xy1, xy2):
        return abs(((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5)

    def get_distance_from_self(self, xy) -> float:
        return self.get_distance_to_point(self.pos, xy)

    def get_distance_to_target(self, target) -> float:
        return self.get_distance_from_self(target.pos)

    def get_closest_ent(self, ents):
        if len(ents) < 1:
            return

        closest = (ents[0])

        for ent in ents:
            if self.get_distance_to_target(ent) < self.get_distance_to_target(closest):
                closest = ent

        return closest

    def update_closest_food(self):
        self.closest_food = self.get_closest_ent(Fish.foods)
        return self.closest_food

    def update_closest_fish(self):
        if len(Fish.fishes) < 1 or self not in Fish.fishes:
            return self

        looklist = Fish.fishes.copy()
        looklist.remove(self)
        self.closest_fish = self.get_closest_ent(looklist)
        return self.closest_fish

    def advance_toward(self, point: tuple, strength: int = 2):

        x, y = self.pos

        if x < point[0]:
            if self.is_within((x + strength, y)):
                self.move(strength, 0)
        elif x > point[0]:
            if self.is_within((x - strength, y)):
                self.move(-strength, 0)

        if y < point[1]:
            if self.is_within((x, y + strength)):
                self.move(0, strength)
        elif y > point[1]:
            if self.is_within((x, y - strength)):
                self.move(0, -strength)

    def advance_away(self, point: tuple, strength: int = 2):
        self.advance_toward(point, -strength)

    def seek_food(self):
        self.update_closest_food()
        if len(Fish.foods) < 0:
            return

        # if self.personality == 2:  # Friendly
        #     self.advance_toward(self.closest_food.pos, 3)
        #     # If fish is friendly, chase food 50% faster
        # else:
        self.advance_toward(self.closest_food.pos)

        if self.get_distance_to_target(self.closest_food) < 2:
            self.eat()
            SOUNDS.get("fish_eat").play()
            Fish.foods.remove(self.closest_food)

    def get_fish_image(self):
        pass

    def wander(self, bubbles, fish):

        if self.get_distance_from_self(self.wander_goal) < 4:
            self.assign_new_wander_goal()

        # All fish actively avoid bubble chasers
        # if self.personality == 0 and self.closest_fish and self.closest_fish.personality == 3 and self.get_distance_to_target(
        #         self.closest_fish) < 50:
        #     self.advance_away(self.closest_fish.pos, 6)
        #
        # if self.personality == 0:
        #     self.advance_toward(self.wander_goal)
        # elif self.personality == 1:  # Timid:
        #
        #     if len(fish) > 1 and self.get_distance_to_target(
        #             self.closest_fish) < 80 and self.closest_fish.personality != 1:
        #         self.advance_away(self.closest_fish.pos, 3)
        #     else:
        #         self.advance_toward(self.wander_goal)
        # elif self.personality == 2:  # Friendly
        #     if len(fish) > 1 and self.get_distance_to_target(self.closest_fish) > 150:
        #         self.advance_toward(self.closest_fish.pos)
        #     else:
        #         self.advance_toward(self.wander_goal)
        # elif self.personality == 3:  # Bubble Chaser
        #     if len(bubbles) > 0 and self.bubble_hunger == 0:
        #         target_bubble = self.get_closest_ent(bubbles)
        #         self.advance_toward(target_bubble.pos, 3)
        #         if self.get_distance_to_target(target_bubble) < 2:
        #             target_bubble.pop(bubbles)
        #             self.bubble_hunger += 400
        #     else:
        #         self.advance_toward(self.wander_goal)

    def draw_nametag(self, screen, color, m_font: pygame.font.SysFont):
        nametag_label = m_font.render(f'Fish{self.name} | {self.hunger}', True, color,
                                      )
        nametag_size = pygame.font.Font.size(m_font, f'Fish{self.name} | {self.hunger}')
        nametag_rect = pygame.Rect(self.pos[0] - nametag_size[0] // 2, self.pos[1] - 15, 20, 10)

        screen.blit(nametag_label, nametag_rect)

    def draw_hunger_bar(self, screen):
        hunger_percent = self.hunger / self.max_hunger
        bg_rect = pygame.Rect(self.pos[0] - 25, self.pos[1] - 15, 75, 5)
        amount_rect = pygame.Rect(self.pos[0] - 25, self.pos[1] - 15, 75 * hunger_percent, 5)
        pygame.draw.rect(screen, (40, 40, 40, 100), bg_rect)
        pygame.draw.rect(screen, (255 - (255 * hunger_percent), (255 * hunger_percent), 50), amount_rect)
        # if self.personality == 3:
        #     bubble_hunger_percent = self.bubble_hunger / self.max_bubble_hunger
        #     bubble_amount_rect = pygame.Rect(self.pos[0] + 16 - (32 * bubble_hunger_percent), self.pos[1] - 20,
        #                                      (75 - 16) * bubble_hunger_percent, 5)
        #     pygame.draw.rect(screen, (255, 255, 0, 80), bubble_amount_rect)

    def draw(self, screen):
        screen.blit(self.get_fish_image(), (self.pos[0] - 16, self.pos[1] - 16))

    def draw_food_target(self, screen, color, foods):
        self.get_closest_ent(foods)
        pygame.draw.line(screen, color, self.pos, self.closest_food.pos)

    def draw_wander_goal(self, screen, color):
        pygame.draw.rect(screen, color, (*self.wander_goal, 7, 7))

    def draw_line_to_wander_goal(self, screen, color):
        pygame.draw.line(screen, color, self.pos, self.wander_goal)

    def run(self):
        self.increase_hunger()
        self.update_closest_fish()
        self.update_closest_food()
        if self.is_hungry() and len(Fish.foods) > 0:
            self.seek_food()
        else:
            self.wander(Fish.bubbles, Fish.fishes)


class BubbleChaserFish(Fish):

    def __init__(self, name, pos: tuple[int, int] = (0, 0),
                 bounds: tuple[int, int] = (100, 100),
                 max_hunger: int = 2500, max_bubble_hunger: int = 800):
        super().__init__(name, pos, bounds, max_hunger)
        self.hunger = self.max_hunger
        self.bounds = bounds
        self.closest_food = None
        self.closest_fish = self
        self.facing_left = False
        self.wander_goal: tuple = (0, 0)
        self.assign_new_wander_goal()
        self.max_bubble_hunger = max_bubble_hunger
        self.bubble_hunger = self.max_bubble_hunger

    def is_hungry(self):
        return self.hunger <= 400

    def increase_hunger(self):
        self.hunger = max(self.hunger - 1, 0)
        self.bubble_hunger = max(self.bubble_hunger - 1, 0)
        if self.hunger == 0:
            self.die()

    def seek_food(self) -> None:
        if len(Fish.foods) < 1:
            return

        self.update_closest_food()
        self.advance_toward(self.closest_food.pos)

        if self.get_distance_to_target(self.closest_food) < 2:
            self.eat()
            SOUNDS.get("fish_eat").play()
            Fish.foods.remove(self.closest_food)

    def get_fish_image(self):
        return pygame.transform.flip(pygame.transform.scale(FISH_IMAGES.get(3), (64, 64)),
                                     self.facing_left, False)

    def draw_hunger_bar(self, screen):
        hunger_percent = self.hunger / self.max_hunger
        bg_rect = pygame.Rect(self.pos[0] - 25, self.pos[1] - 15, 75, 5)
        amount_rect = pygame.Rect(self.pos[0] - 25, self.pos[1] - 15, 75 * hunger_percent, 5)
        pygame.draw.rect(screen, (40, 40, 40, 100), bg_rect)
        pygame.draw.rect(screen, (255 - (255 * hunger_percent), (255 * hunger_percent), 50), amount_rect)

        bubble_hunger_percent = self.bubble_hunger / self.max_bubble_hunger
        bubble_amount_rect = pygame.Rect(self.pos[0] + 16 - (32 * bubble_hunger_percent), self.pos[1] - 20,
                                         (75 - 16) * bubble_hunger_percent, 5)
        pygame.draw.rect(screen, (255, 255, 0, 80), bubble_amount_rect)

    def wander(self, bubbles, fish):

        if self.get_distance_from_self(self.wander_goal) < 4:
            self.assign_new_wander_goal()

        if len(bubbles) > 0 and self.bubble_hunger == 0:
            target_bubble = self.get_closest_ent(bubbles)
            self.advance_toward(target_bubble.pos, 3)
            if self.get_distance_to_target(target_bubble) < 2:
                target_bubble.pop(bubbles)
                self.bubble_hunger += 400
        else:
            self.advance_toward(self.wander_goal)

    def run(self):
        self.increase_hunger()
        self.update_closest_fish()
        self.update_closest_food()
        if self.is_hungry() and len(Fish.foods) > 0:
            self.seek_food()
        else:
            self.wander(Fish.bubbles, Fish.fishes)


class NeutralFish(Fish):

    def __init__(self, name, pos: tuple[int, int] = (0, 0),
                 bounds: tuple[int, int] = (100, 100),
                 max_hunger: int = 2500):
        super().__init__(name, pos, bounds, max_hunger)
        self.hunger = self.max_hunger
        self.bounds = bounds
        self.closest_food = None
        self.closest_fish = self
        self.facing_left = False
        self.wander_goal: tuple = (0, 0)
        self.assign_new_wander_goal()

    def seek_food(self) -> None:
        if len(Fish.foods) < 1:
            return

        self.update_closest_food()
        self.advance_toward(self.closest_food.pos)

        if self.get_distance_to_target(self.closest_food) < 2:
            self.eat()
            SOUNDS.get("fish_eat").play()
            Fish.foods.remove(self.closest_food)

    def get_fish_image(self):
        return pygame.transform.flip(pygame.transform.scale(FISH_IMAGES.get(0), (64, 64)),
                                     self.facing_left, False)

    def wander(self, bubbles, fish):

        if self.get_distance_from_self(self.wander_goal) < 4:
            self.assign_new_wander_goal()

        if self.closest_fish and isinstance(self.closest_fish, BubbleChaserFish) and self.get_distance_to_target(
                self.closest_fish) < 50:
            self.advance_away(self.closest_fish.pos, 6)
        else:
            self.advance_toward(self.wander_goal)

    def run(self):
        self.increase_hunger()
        self.update_closest_fish()
        self.update_closest_food()
        if self.is_hungry() and len(Fish.foods) > 0:
            self.seek_food()
        else:
            self.wander(Fish.bubbles, Fish.fishes)


class TimidFish(Fish):

    def __init__(self, name, pos: tuple[int, int] = (0, 0), bounds: tuple[int, int] = (100, 100),
                 max_hunger: int = 2500):
        super().__init__(name, pos, bounds, max_hunger)
        self.hunger = self.max_hunger
        self.bounds = bounds
        self.closest_food = None
        self.closest_fish = self
        self.facing_left = False
        self.wander_goal: tuple = (0, 0)
        self.assign_new_wander_goal()

    def assign_new_wander_goal(self) -> None:
        self.wander_goal = self.get_random_map_point()

        center = (self.bounds[0] // 2, self.bounds[1] // 2)
        while self.get_distance_to_point(self.wander_goal, center) < 500:
            self.wander_goal = self.get_random_map_point()

    def seek_food(self):
        self.update_closest_food()
        if len(Fish.foods) < 0:
            return

        self.advance_toward(self.closest_food.pos)

        if self.get_distance_to_target(self.closest_food) < 2:
            self.eat()
            SOUNDS.get("fish_eat").play()
            Fish.foods.remove(self.closest_food)

    def get_fish_image(self):
        return pygame.transform.flip(pygame.transform.scale(FISH_IMAGES.get(1), (64, 64)),
                                     self.facing_left, False)

    def wander(self, bubbles, fish):

        if self.get_distance_from_self(self.wander_goal) < 4:
            self.assign_new_wander_goal()

        if len(fish) > 1 and self.get_distance_to_target(self.closest_fish) < 80:
            self.advance_away(self.closest_fish.pos, 3)
        else:
            self.advance_toward(self.wander_goal)

    def run(self):
        self.increase_hunger()
        self.update_closest_fish()
        self.update_closest_food()
        if self.is_hungry() and len(Fish.foods) > 0:
            self.seek_food()
        else:
            self.wander(Fish.bubbles, Fish.fishes)


class FriendlyFish(Fish):

    def __init__(self, name, pos: tuple[int, int] = (0, 0), bounds: tuple[int, int] = (100, 100),
                 max_hunger: int = 2500):
        super().__init__(name, pos, bounds, max_hunger)
        self.hunger = self.max_hunger
        self.bounds = bounds
        self.closest_food = None
        self.closest_fish = self
        self.facing_left = False
        self.wander_goal: tuple = (0, 0)
        self.assign_new_wander_goal()

    def assign_new_wander_goal(self) -> None:
        self.wander_goal = self.get_random_map_point()

        center = (self.bounds[0] // 2, self.bounds[1] // 2)
        while self.get_distance_to_point(self.wander_goal, center) > 200:
            self.wander_goal = self.get_random_map_point()

    def seek_food(self):
        self.update_closest_food()
        if len(Fish.foods) < 0:
            return

        # If fish is friendly, chase food ~50% faster
        self.advance_toward(self.closest_food.pos, 3)

        if self.get_distance_to_target(self.closest_food) < 2:
            self.eat()
            SOUNDS.get("fish_eat").play()
            Fish.foods.remove(self.closest_food)

    def get_fish_image(self):
        return pygame.transform.flip(pygame.transform.scale(FISH_IMAGES.get(2), (64, 64)),
                                     self.facing_left, False)

    def wander(self, bubbles, fish):

        if self.get_distance_from_self(self.wander_goal) < 4:
            self.assign_new_wander_goal()

        if len(fish) > 1 and self.get_distance_to_target(self.closest_fish) > 150:
            self.advance_toward(self.closest_fish.pos)
        else:
            self.advance_toward(self.wander_goal)

    def run(self):
        self.increase_hunger()
        self.update_closest_fish()
        self.update_closest_food()
        if self.is_hungry() and len(Fish.foods) > 0:
            self.seek_food()
        else:
            self.wander(Fish.bubbles, Fish.fishes)

