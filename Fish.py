import random
import pygame


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

    def rise(self, bubbles):
        if self.pos[1] + 8 > 0:
            self.pos = (self.pos[0] + random.randint(-1, 1), self.pos[1] - 1)
        else:
            bubbles.remove(self)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255, 80), self.pos, self.radius, 1)
        pygame.draw.circle(screen, (255, 255, 255, 80), self.pos, self.radius - self.shine_amount, self.shine_amount,
                           draw_top_left=self.shines[self.shine][0], draw_top_right=self.shines[self.shine][1],
                           draw_bottom_left=self.shines[self.shine][2], draw_bottom_right=self.shines[self.shine][3])


class Food:

    def __init__(self, pos: tuple[int, int] = (0, 0), y_limit: int = 0, nutrition: int = 1000):
        self.pos = pos
        self.floor = y_limit
        self.nutrition = nutrition

    def fall(self):
        if self.pos[1] + 8 < self.floor:
            self.pos = (self.pos[0] + random.randint(-1, 1), self.pos[1] + 1)

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, (*self.pos, 8, 8))


class Fish:
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
            "description": "This fish does not wander like the rest. They only want to chase bubbles. They will eat "
                           "only when necessary."}
    }

    def __init__(self, name, pos: tuple[int, int] = (0, 0), bounds: tuple[int, int] = (100, 100), hunger: int = 1000,
                 personality: int = 0):
        self.name = name
        self.pos = pos
        self.hunger = hunger
        self.bounds = bounds
        self.closest_food = None
        self.closest_fish = None
        self.wander_goal: tuple = (0, 0)
        self.personality = personality
        self.assign_new_wander_goal()

    def eat(self):
        self.hunger += 1000

    def increase_hunger(self):
        self.hunger = max(self.hunger - 1, 0)

    @staticmethod
    def food_exists(foods):
        return len(foods) > 0

    def is_hungry(self):
        return self.hunger <= 700

    def is_within(self) -> bool:
        return not (self.pos[0] <= 0 or self.pos[0] >= self.bounds[0] or self.bounds[1] <= 0 or self.bounds[1] >=
                    self.bounds[1])

    def get_random_map_point(self):
        return random.randrange(0, self.bounds[0]), random.randrange(0, self.bounds[1])

    def assign_new_wander_goal(self) -> None:
        self.wander_goal = self.get_random_map_point()

        if self.personality == 1:  # Timid
            center = (self.bounds[0] // 2, self.bounds[1] // 2)
            while self.get_distance_to_point(self.wander_goal, center) < 500:
                self.wander_goal = self.get_random_map_point()
        elif self.personality == 2:  # Friendly
            center = (self.bounds[0] // 2, self.bounds[1] // 2)
            while self.get_distance_to_point(self.wander_goal, center) > 200:
                self.wander_goal = self.get_random_map_point()

    def get_distance_to_point(self, xy1, xy2):
        return abs(((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5)

    def get_distance_from_self(self, xy) -> float:
        return self.get_distance_to_point(self.pos, xy)

    def get_distance_to_target(self, target: Food) -> float:
        return self.get_distance_from_self(target.pos)

    def get_closest_ent(self, ents):
        if len(ents) < 1:
            return

        closest = (ents[0])

        for ent in ents:
            if self.get_distance_to_target(ent) < self.get_distance_to_target(closest):
                closest = ent

        return closest

    def get_closest_food(self, foods):
        self.closest_food = self.get_closest_ent(foods)
        return self.closest_food

    def get_closest_fish(self, fish):
        self.closest_fish = self.get_closest_ent(fish)
        return self.closest_fish

    def advance_toward(self, point: tuple, strength: int = 2):

        x, y = self.pos

        if x < point[0]:
            x += strength
        elif x > point[0]:
            x -= strength
        else:
            pass

        if y < point[1]:
            y += strength
        elif y > point[1]:
            y -= strength
        else:
            pass

        self.pos = (x, y)

    def advance_away(self, point: tuple, strength: int = 2):
        self.advance_toward(point, -strength)

    def seek_food(self, foods: list[Food]):
        self.get_closest_food(foods)
        if not self.food_exists(foods):
            return

        if self.personality == 2:  # Friendly
            self.advance_toward(self.closest_food.pos, 3)
            # If fish is friendly, chase food 50% faster
        else:
            self.advance_toward(self.closest_food.pos)

        if self.get_distance_to_target(self.closest_food) < 2:
            self.eat()
            foods.remove(self.closest_food)

    def wander(self, fish, food, bubbles):
        seed = random.randint(0, 3)
        if self.get_distance_from_self(self.wander_goal) < 4:
            self.assign_new_wander_goal()
        if seed == 1:
            if self.personality == 3:
                if len(bubbles) > 0:
                    self.wander_goal = self.get_closest_ent(bubbles).pos
                else:
                    self.get_random_map_point()
            self.advance_toward(self.wander_goal, 2)

        elif seed == 2:
            self.get_closest_fish(fish)
            if self.personality == 1:  # Timid:
                if self.get_distance_from_self(self.closest_fish.pos) < 30:
                    self.advance_away(self.closest_fish.pos, 12)
            elif self.personality == 2:  # Friendly
                self.advance_toward(self.closest_fish.pos)
            elif self.personality == 3:
                self.advance_toward(self.wander_goal, 6)
            self.pos = (self.pos[0] + random.randint(-1, 1), self.pos[1] + random.randint(-1, 1))
        else:
            pass

    def draw(self, screen, color, font):
        nametag_rect = pygame.Rect(self.pos[0], self.pos[1] - 15, 20, 10)
        nametag_label = font.render(f'Fish{self.name} | {self.hunger} | {self.personality}', True, color,
                                    )
        screen.blit(nametag_label, nametag_rect)
        pygame.draw.rect(screen, color, (*self.pos, 18, 18))

    def draw_food_target(self, screen, color, foods):
        self.get_closest_ent(foods)
        pygame.draw.line(screen, color, self.pos, self.closest_food.pos)

    def draw_wander_goal(self, screen, color):
        pygame.draw.rect(screen, color, (*self.wander_goal, 7, 7))

    def draw_line_to_wander_goal(self, screen, color):
        pygame.draw.line(screen, color, self.pos, self.wander_goal)

    def run(self, fish: list, foods: list[Food], bubbles: list[Bubble]):
        self.increase_hunger()
        if self.is_hungry() and len(foods) > 0:
            self.seek_food(foods)
        else:
            self.wander(fish, foods, bubbles)
