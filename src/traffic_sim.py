import pygame
import time
import random
import sys
from config import *
from vehicle import *

class TrafficSim:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Traffic Simulator")
        self.traffic_lights = {
            "top": 1,
            "bottom": 1,
            "left": 1,
            "right": 1
        }
        self.last_toggle_time = {
            "top": 2,
            "bottom": 2,
            "left": 2,
            "right": 2
        }
        self.cars = []
        self.last_creation_time = time.time()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)


    def process_events(self) -> bool:
        """Allows user to toggle traffic lights with arrow keys and checks for quit events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.toggle_light("top")
                elif event.key == pygame.K_DOWN:
                    self.toggle_light("bottom")
                elif event.key == pygame.K_LEFT:
                    self.toggle_light("left")
                elif event.key == pygame.K_RIGHT:
                    self.toggle_light("right")
        return True


    def draw_roads(self) -> None:
        # Vertical road
        pygame.draw.rect(self.screen, GRAY, (WIDTH//2 - ROAD_WIDTH//2, 0, ROAD_WIDTH, HEIGHT))
        # Horizontal road
        pygame.draw.rect(self.screen, GRAY, (0, HEIGHT//2 - ROAD_WIDTH//2, WIDTH, ROAD_WIDTH))
        # Lane dividers
        pygame.draw.line(self.screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
        pygame.draw.line(self.screen, WHITE, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)

    def draw_traffic_light(self, x: int, y: int, color: int) -> None:
        pygame.draw.rect(self.screen, WHITE, (x, y, LIGHT_BOX_WIDTH, LIGHT_BOX_HEIGHT))
        colors = [BLACK, BLACK, BLACK]
        if color == 0:
            colors[0] = RED
        if color == 1:
            colors[1] = GREEN
    
        # Draw individuals lights inside the box
        for index, col in enumerate(colors):
            pygame.draw.circle(self.screen, col, (x + LIGHT_BOX_WIDTH // 2, y + LIGHT_SPACING + index * (LIGHT_SIZE + LIGHT_SPACING)
                                                    + LIGHT_SIZE // 2), LIGHT_SIZE // 2)
            
    def draw_car(self, car) -> None:
        pygame.draw.circle(self.screen, RED, (car.x, car.y), car.radius)

    def create_car(self) -> Veh:
        direction = random.choice(DIRECTIONS)
        match direction:
            # Left to Right
            case 0:
                return Veh(0, HEIGHT // 2 + LANE_WIDTH // 2, direction)
            # Bottom to Top
            case 1:
                return Veh(WIDTH // 2 + LANE_WIDTH // 2, HEIGHT, direction)
            # Right to Left
            case 2:
                return Veh(WIDTH, HEIGHT // 2 - LANE_WIDTH // 2, direction)
            # Top to Bottom
            case 3:
                return Veh(WIDTH // 2 - LANE_WIDTH // 2, 0, direction)
            
    def toggle_light(self, direction) -> None:
        current_time = time.time()
        if current_time - self.last_toggle_time[direction] < 2:
            return
        
        current_state = self.traffic_lights[direction]
        self.traffic_lights[direction] = 1 - current_state
    
        # Update the last toggle time for this light
        self.last_toggle_time[direction] = current_time
            
    def check_traffic(self):
        stop_offset = 3
        for car in self.cars:
            match car.direction:
                # Left to Right
                case 0:
                    if not car.passed_intersection and self.traffic_lights["left"] == 0 and car.x > LIGHT_LEFT_X:
                        car.speed = 0
                    else:
                        car.speed = CAR_SPEED
                        if car.x >= LIGHT_BOTTOM_X + stop_offset:
                            car.passed_intersection = True
                # Bottom to Top
                case 1:
                    if not car.passed_intersection and self.traffic_lights["bottom"] == 0 and car.y < LIGHT_BOTTOM_Y:
                        car.speed = 0
                    else:
                        car.speed = CAR_SPEED
                        if car.y <= LIGHT_BOTTOM_Y - stop_offset:
                            car.passed_intersection = True
                # Right to Left
                case 2:
                    if not car.passed_intersection and self.traffic_lights["right"] == 0 and car.x < LIGHT_RIGHT_X:
                        car.speed = 0
                    else:
                        car.speed = CAR_SPEED
                        if car.x <= LIGHT_RIGHT_X - stop_offset:
                            car.passed_intersection = True
                # Top to Bottom
                case 3:
                    if not car.passed_intersection and self.traffic_lights["top"] == 0 and car.y > LIGHT_TOP_Y:
                        car.speed = 0
                    else:
                        car.speed = CAR_SPEED
                        if car.y >= LIGHT_TOP_Y + stop_offset:
                            car.passed_intersection = True

    def check_collision(self) -> bool:
        for i, car1 in enumerate(self.cars):
            for car2 in self.cars[i+1:]:
                dx = car1.x - car2.x
                dy = car1.y - car2.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < car1.radius + car2.radius and car1.direction != car2.direction:
                    return True
        return False
    
    def reset(self) -> None:
        self.cars = []
        self.traffic_lights = {
        "top": 1,
        "bottom": 1,
        "left": 1,
        "right": 1
        }
        self.last_toggle_time = {
            "top": 2,
            "bottom": 2,
            "left": 2,
            "right": 2
        }

    def check_car_out_of_bounds(self, car) -> bool:
        out_left = car.direction == 0 and car.x > WIDTH
        out_bottom = car.direction == 1 and car.y < 0
        out_right = car.direction == 2 and car.x < 0
        out_top = car.direction == 3 and car.y > HEIGHT
        return out_left or out_right or out_bottom or out_top
        

    def update_simulation(self) -> None:
        for car in self.cars:
            self.check_traffic()
            car.move(self.cars)
            
        current_time = time.time()
        if current_time - self.last_creation_time >= CAR_SPAWN_RATE:
            self.cars.append(self.create_car())
            self.last_creation_time = time.time()

        self.cars = [car for car in self.cars if not self.check_car_out_of_bounds(car)]

    def render(self, episode_number) -> None:
        self.screen.fill(BLACK)
        
        self.draw_roads()
        self.draw_traffic_light(LIGHT_LEFT_X, LIGHT_LEFT_Y, self.traffic_lights["left"])
        self.draw_traffic_light(LIGHT_RIGHT_X, LIGHT_RIGHT_Y, self.traffic_lights["right"])
        self.draw_traffic_light(LIGHT_TOP_X, LIGHT_TOP_Y, self.traffic_lights["top"])
        self.draw_traffic_light(LIGHT_BOTTOM_X, LIGHT_BOTTOM_Y, self.traffic_lights["bottom"])

        # Render episode number
        text_surface = self.font.render(f"Episode: {episode_number}", True, WHITE)
        text_rect = text_surface.get_rect(topright=(WIDTH - 10, 10))
        self.screen.blit(text_surface, text_rect)
        
        for car in self.cars:
            self.draw_car(car)
        pygame.display.flip()
        self.clock.tick(FPS)