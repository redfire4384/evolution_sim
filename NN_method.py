import numpy as np
import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

class Herbivore:
    def __init__(self, x, y, color=(155, 40, 155), neural_network=None):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = color
        self.r = self.color[0]
        self.g = self.color[1]
        self.b = self.color[2]
        self.speed = 20
        self.health = 100
        self.lerp_t = 0
        self.lerp_duration = 1
        self.target_x = x
        self.target_y = y
        self.neural_network = neural_network or self.create_neural_network()

    def lerp(self, start, end, t):
        return start + t * (end - start)

    def softmax(self, it):
        e_it = np.exp(it - np.max(it))
        return e_it / e_it.sum()

    def create_neural_network(self):
        # Create a simple neural network with input, hidden, and output layers
        input_layer = np.random.randn(4, 5)
        hidden_layer = np.random.randn(5, 5)
        output_layer = np.random.randn(5, 3)
        return [input_layer, hidden_layer, output_layer]

    def mutate(self):
        # Mutate the neural network by adding small random values
        for layer in self.neural_network:
            layer += np.random.normal(0, 0.1, layer.shape)

        self.color = (
            max(0, min(255, random.randint(self.r - 10, self.r + 10))),
            max(0, min(255, random.randint(self.g - 10, self.g + 10))),
            max(0, min(255, random.randint(self.b - 10, self.b + 10)))
        )

    def update_position(self, nearest_plant):
        # Calculate the input features for the neural network
        input_features = np.array([
            (nearest_plant.x - self.x),
            (nearest_plant.y - self.y),
            self.health,
        ])

        # Calculate the output of the neural network
        input_layer, hidden_layer, output_layer = self.neural_network
        hidden_output = np.tanh(input_features @ input_layer)
        output = self.softmax(hidden_output @ output_layer)  # Apply softmax after multiplying with output layer

        random_move = output[0]
        food_move = output[1]
        none_move = output[2]

        # Calculate where organism moves
        distance_x = nearest_plant.x - self.x
        distance_y = nearest_plant.y - self.y
        distance = (distance_x**2 + distance_y**2)**0.5

        choice = random.choices(['random', 'food', None], weights=[random_move, food_move, none_move])[0]

        if choice == 'random':
            self.target_x = self.x + random.randint(-abs(self.speed), abs(self.speed))
            self.target_y = self.y + random.randint(-abs(self.speed), abs(self.speed))
            self.lerp_t = 0
            self.health -= 1

        elif choice == 'food':
            self.target_x = self.x + (distance_x / distance) * self.speed
            self.target_y = self.y + (distance_y / distance) * self.speed
            self.lerp_t = 0
            self.health -= 1

        if self.lerp_t < 1:
            self.lerp_t += 1 / (self.lerp_duration * 60)
            self.x = self.lerp(self.x, self.target_x, self.lerp_t)
            self.y = self.lerp(self.y, self.target_y, self.lerp_t)

def reproduce_and_mutate(herbs):
    if herbs == []:
        pass
    else:
        selected_herb = random.choice(herbs)
        if random.randint(0, 40) == 0:
            child_neural_network = [layer.copy() for layer in selected_herb.neural_network]
            child = Herbivore(selected_herb.x, selected_herb.y, neural_network=child_neural_network)
            child.mutate()

            # Add the child to the herbivores list
            herbs.append(child)

class Plant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 3
        self.color = (0, 255, 0)

def find_closest_plant(herb, plants):
    closest_plant = None
    closest_distance = float('inf')
    for plant in plants:
        distance = math.sqrt((herb.x - plant.x)**2 + (herb.y - plant.y)**2)
        if distance < closest_distance:
            closest_distance = distance
            closest_plant = plant
    return closest_plant

def draw_plants(plants, screen):
    for plant in plants:
        pygame.draw.circle(screen, plant.color, (plant.x, plant.y), plant.radius)

max_plants = 100
def spawn_plants(plants):
    while len(plants) < max_plants:
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        plants.append(Plant(x, y))

def check_collision_and_health(herbs, plants):
    for herb in herbs:
        if herb.health <= 0:
            herbs.remove(herb)
        for plant in plants:
            distance = math.sqrt((herb.x - plant.x)**2 + (herb.y - plant.y)**2)
            if distance <= herb.radius + plant.radius:
                herb.health += 30
                plants.remove(plant)


def main():
    herbs = [Herbivore(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(5)]
    plants = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        spawn_plants(plants)
        draw_plants(plants, screen)

        for herb in herbs:
            pygame.draw.circle(screen, herb.color, (herb.x, herb.y), herb.radius)
        
            near_plant = find_closest_plant(herb, plants)
            herb.update_position(near_plant)

        check_collision_and_health(herbs, plants)
        reproduce_and_mutate(herbs)

        pygame.display.flip()
        clock.tick(60)
        screen.fill((0,0,0))
    
    
if __name__ == "__main__":
    main()
