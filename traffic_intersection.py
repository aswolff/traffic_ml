import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Screen dimensions
WIDTH = 600
HEIGHT = 600

# Road dimensions
ROAD_WIDTH = 100
LANE_WIDTH = ROAD_WIDTH // 2

# Traffic light dimensions
LIGHT_SIZE = 15
LIGHT_SPACING = 5
LIGHT_BOX_HEIGHT = 3 * LIGHT_SIZE + 4 * LIGHT_SPACING
LIGHT_BOX_WIDTH = LIGHT_SIZE + 2 * LIGHT_SPACING

CAR_REWARD = 10
WAITING_PENALTY = 0.1  # The amount to decrease the score by per second of waiting
SCORE = 0

# Create a display surface
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Perpendicular Roads with Traffic Lights")

def draw_roads():
    # Vertical road
    pygame.draw.rect(screen, GRAY, (WIDTH//2 - ROAD_WIDTH//2, 0, ROAD_WIDTH, HEIGHT))
    # Horizontal road
    pygame.draw.rect(screen, GRAY, (0, HEIGHT//2 - ROAD_WIDTH//2, WIDTH, ROAD_WIDTH))
    # Draw lane dividers
    pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
    pygame.draw.line(screen, WHITE, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)

def draw_traffic_light(x, y, color):
    # Draw the light box
    pygame.draw.rect(screen, WHITE, (x, y, LIGHT_BOX_WIDTH, LIGHT_BOX_HEIGHT))
    colors = [BLACK, BLACK, BLACK]  # default all off
    if color == "red":
        colors[0] = RED
    elif color == "yellow":
        colors[1] = YELLOW
    elif color == "green":
        colors[2] = GREEN

    # Draw individual lights inside the box
    for index, col in enumerate(colors):
        pygame.draw.circle(screen, col, (x + LIGHT_BOX_WIDTH // 2, y + LIGHT_SPACING + index * (LIGHT_SIZE + LIGHT_SPACING) + LIGHT_SIZE // 2), LIGHT_SIZE // 2)

class Car:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 5  # Reduced speed
        self.radius = 10  # Car size
        self.waiting_time = 0
        self.passed_intersection = False  # Add this line

    def move(self):
        global SCORE
        stop_offset = 100  # Distance before the intersection to stop

        # Check for other cars in the same lane
        stop_due_to_other_car = False
        for car in cars:
            if car != self:
                if self.direction in ["north", "south"]:
                    if abs(self.y - car.y) < self.radius * 2 and self.x == car.x:
                        stop_due_to_other_car = True
                        break
                else:
                    if abs(self.x - car.x) < self.radius * 2 and self.y == car.y:
                        stop_due_to_other_car = True
                        break

        if stop_due_to_other_car:
            self.speed = 0
        else:
            self.speed = 5  # Reset speed if no cars in front

        if self.direction == "north":
            if not self.passed_intersection and traffic_lights["south"] == "red" and HEIGHT//2 - LIGHT_BOX_HEIGHT//2 + stop_offset >= self.y - self.radius >= HEIGHT//2:
                self.speed = 0
            else:
                self.y -= self.speed
                if self.y <= HEIGHT // 2:
                    self.passed_intersection = True

        elif self.direction == "south":
            if not self.passed_intersection and traffic_lights["north"] == "red" and HEIGHT//2 + ROAD_WIDTH//2 - stop_offset <= self.y + self.radius <= HEIGHT//2 + ROAD_WIDTH//2:
                self.speed = 0
            else:
                self.y += self.speed
                if self.y >= HEIGHT // 2:
                    self.passed_intersection = True

        elif self.direction == "west":
            if not self.passed_intersection and traffic_lights["east"] == "red" and WIDTH//2 - LIGHT_BOX_HEIGHT//2 + stop_offset >= self.x - self.radius >= WIDTH//2:
                self.speed = 0
            else:
                self.x -= self.speed
                if self.x <= WIDTH // 2:
                    self.passed_intersection = True

        elif self.direction == "east":
            if not self.passed_intersection and traffic_lights["west"] == "red" and WIDTH//2 + ROAD_WIDTH//2 - stop_offset <= self.x + self.radius <= WIDTH//2 + ROAD_WIDTH//2:
                self.speed = 0
            else:
                self.x += self.speed
                if self.x >= WIDTH // 2:
                    self.passed_intersection = True

        if self.speed == 0:  # If the car is stopped
            self.waiting_time += 1/60  # Increase the waiting time (assuming 60 FPS)




    def draw(self):
        pygame.draw.circle(screen, (255, 165, 0), (self.x, self.y), self.radius)

    def collides_with(self, other_car):
        distance = ((self.x - other_car.x)**2 + (self.y - other_car.y)**2)**0.5
        return distance < 1*self.radius

def create_car():
    direction = random.choice(["north", "south", "east", "west"])
    if direction == "north":
        return Car(WIDTH // 2 + LANE_WIDTH // 2, HEIGHT, direction)
    elif direction == "south":
        return Car(WIDTH // 2 - LANE_WIDTH // 2, 0, direction)
    elif direction == "east":
        return Car(0, HEIGHT // 2 + LANE_WIDTH // 2, direction)
    elif direction == "west":
        return Car(WIDTH, HEIGHT // 2 - LANE_WIDTH // 2, direction)

    
traffic_lights = {
    "north": "green",
    "south": "green",
    "east": "green",
    "west": "green"
}

cars = []

def check_for_collisions():
    for i in range(len(cars)):
        for j in range(i+1, len(cars)):
            if cars[i].collides_with(cars[j]):
                return True
    return False

def toggle_light(direction):
    # Get the current state of the light
    current_state = traffic_lights[direction]
    # Toggle the light's state
    if current_state == "green":
        traffic_lights[direction] = "red"
    else:
        traffic_lights[direction] = "green"

def main():
    global cars, SCORE
    last_creation_time = time.time()
    clock = pygame.time.Clock()  # Introduce a clock for framerate control
    while True:
        current_time = time.time()
        if current_time - last_creation_time >= 2:  # Every 2 seconds
            cars.append(create_car())
            last_creation_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Up arrow
                    toggle_light("north")
                elif event.key == pygame.K_DOWN:  # Down arrow
                    toggle_light("south")
                elif event.key == pygame.K_LEFT:  # Left arrow
                    toggle_light("west")
                elif event.key == pygame.K_RIGHT:  # Right arrow
                    toggle_light("east")

        screen.fill(BLACK)
        draw_roads()

        # Draw traffic lights
        draw_traffic_light(WIDTH//2 - ROAD_WIDTH//2 - LIGHT_BOX_WIDTH - 10, HEIGHT//2 - LIGHT_BOX_HEIGHT//2, traffic_lights["west"])
        draw_traffic_light(WIDTH//2 + ROAD_WIDTH//2 + 10, HEIGHT//2 - LIGHT_BOX_HEIGHT//2, traffic_lights["east"])
        draw_traffic_light(WIDTH//2 - LIGHT_BOX_WIDTH//2, HEIGHT//2 - ROAD_WIDTH//2 - LIGHT_BOX_HEIGHT - 10, traffic_lights["north"])
        draw_traffic_light(WIDTH//2 - LIGHT_BOX_WIDTH//2, HEIGHT//2 + ROAD_WIDTH//2 + 10, traffic_lights["south"])

        # Update and draw cars
        for car in cars:
            car.move()
            car.draw()
            #SCORE -= car.waiting_time * WAITING_PENALTY

        if check_for_collisions():
            cars = []  # Empty the list of cars
            SCORE = 0  # Reset the score
            continue  # Continue to the next iteration of the while loop

        # Display the score on the screen
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Score: {int(SCORE)}', True, WHITE)
        screen.blit(score_text, (10, 10))



        pygame.display.flip()
        clock.tick(60)  # Set a framerate of 60 FPS

if __name__ == '__main__':
    main()
