import random
import pygame


class Food:

    def __init__(self, pos: tuple[int, int] = (0, 0), y_limit: int = 0):
        self.pos = pos
        self.floor = y_limit

    def fall(self):
        if self.pos[1] + 8 < self.floor:
            self.pos = (self.pos[0] + random.randint(-1, 1), self.pos[1] + 1)

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, (*self.pos, 8, 8))


class Fish:

    def __init__(self, name, pos: tuple[int, int] = (0, 0), bounds: tuple[int, int] = (100, 100), hunger: int = 1000):
        self.name = name
        self.pos = pos
        self.hunger = hunger
        self.bounds = bounds
        self.closest = None

    def eat(self):
        self.hunger += 1000

    def increase_hunger(self):
        self.hunger = max(self.hunger - 1, 0)

    def is_hungry(self):
        return self.hunger <= 700

    def is_within(self) -> bool:
        return not (self.pos[0] <= 0 or self.pos[0] >= self.bounds[0] or self.bounds[1] <= 0 or self.bounds[1] >=
                    self.bounds[1])

    def get_random_map_point(self) -> tuple[int, int]:
        return random.randrange(0, self.bounds[0]), random.randrange(0, self.bounds[1])

    def get_distance_to_point(self, x, y) -> float:
        return abs(((self.pos[0] - x) ** 2 + (self.pos[1] - y) ** 2) ** 0.5)

    def get_distance_to_target(self, target: Food) -> float:
        return self.get_distance_to_point(target.pos[0], target.pos[1])

    def get_closest_food(self, foods: list[Food]):
        closest = (foods[0])

        for pellet in foods:
            if self.get_distance_to_target(pellet) < self.get_distance_to_target(closest):
                closest = pellet
        self.closest = closest
        return closest

    def advance_toward(self, point: tuple[int, int], strength: int = 2):

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

    def seek_food(self, foods: list[Food]):
        self.get_closest_food(foods)
        if len(foods) == 0:
            return
        self.advance_toward(self.closest.pos)

        if self.get_distance_to_target(self.closest) < 2:
            self.eat()
            foods.remove(self.closest)

    def wander(self):
        if random.randint(0, 10) == 1:
            self.advance_toward(self.get_random_map_point(), 4)

    def draw(self, screen, color, font, foods):
        nametag_rect = pygame.Rect(self.pos[0], self.pos[1] - 15, 20, 10)
        nametag_label = font.render(f'Fish{self.name} | {self.hunger}', True, (255, 255, 255, 255), True)
        screen.blit(nametag_label, nametag_rect)
        pygame.draw.rect(screen, color, (*self.pos, 18, 18))

        #self.get_closest_food(foods)
        #pygame.draw.line(screen, (255, 255, 255), self.pos, self.closest.pos)

    def run(self, foods: list[Food]):
        self.increase_hunger()
        if self.is_hungry() and len(foods) > 0:
            self.seek_food(foods)
        else:
            self.wander()
