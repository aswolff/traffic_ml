import random
import pygame
import time
import sys
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO 
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
import pygame.font

# Screen Dimensions
WIDTH = 800
HEIGHT = 800

# Road dimensions
ROAD_WIDTH = 100
LANE_WIDTH = ROAD_WIDTH // 2

# Traffic light dimensions
LIGHT_SIZE = 15
LIGHT_SPACING = 5
LIGHT_BOX_HEIGHT = 3 * LIGHT_SIZE + 4 * LIGHT_SPACING
LIGHT_BOX_WIDTH = LIGHT_SIZE + 2 * LIGHT_SPACING

# Default Car start positions, directions
START_POS = [[-WIDTH//2, 0], [0, HEIGHT//2], [WIDTH//2, 0], [0, -HEIGHT//2]]
DIRECTIONS = [0, 1, 2, 3]

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

class veh:
    def __init__(self, x: int, y: int, direction: int):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 1
        self.radius = 10
        self.waiting_time = 0
        self.passed_intersection = False

    def move(self, cars: list['veh']) -> None: 
        stop_offset = 20

        # Stop if there is a car in front of the current one
        for other_car in cars:
            if self != other_car:
                if self.direction == other_car.direction:
                    if self.direction == 0 and other_car.x > self.x and (other_car.x - self.x) < stop_offset:
                        self.speed = 0
                        return
                    elif self.direction == 2 and other_car.x < self.x and (self.x - other_car.x) < stop_offset:
                        self.speed = 0
                        return
                    elif self.direction == 1 and other_car.y < self.y and (self.y - other_car.y) < stop_offset:
                        self.speed = 0
                        return
                    elif self.direction == 3 and other_car.y > self.y and (other_car.y - self.y) < stop_offset:
                        self.speed = 0
                        return

        match self.direction:
            case 0:
                self.x += self.speed
            case 1:
                self.y -= self.speed
            case 2:
                self.x -= self.speed
            case 3:
                self.y += self.speed

        if self.speed == 0:
            self.waiting_time += 1/60

class trafficsim:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Traffic Sim")
        self.traffic_lights = {
            "top": "green",
            "bottom": "green",
            "left": "green",
            "right": "green"
        }
        self.cars = []
        self.last_creation_time = time.time()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.toggle_light("top")
                elif event.key == pygame.K_DOWN:
                    self.toggle_light("bottom")
                elif event.key == pygame.K_LEFT:
                    self.toggle_light("left")
                elif event.key == pygame.K_RIGHT:
                    self.toggle_light("right")

    def draw_roads(self):
        # Vertical road
        pygame.draw.rect(self.screen, GRAY, (WIDTH//2 - ROAD_WIDTH//2, 0, ROAD_WIDTH, HEIGHT))
        # Horizontal road
        pygame.draw.rect(self.screen, GRAY, (0, HEIGHT//2 - ROAD_WIDTH//2, WIDTH, ROAD_WIDTH))
        # Draw lane dividers
        pygame.draw.line(self.screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
        pygame.draw.line(self.screen, WHITE, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)

    def draw_traffic_light(self, x: int, y: int, color: str):
        # Draw the light box
        pygame.draw.rect(self.screen, WHITE, (x, y, LIGHT_BOX_WIDTH, LIGHT_BOX_HEIGHT))
        colors = [BLACK, BLACK, BLACK]  # default all off
        if color == "red":
            colors[0] = RED
        elif color == "yellow":
            colors[1] = YELLOW
        elif color == "green":
            colors[2] = GREEN

        # Draw individual lights inside the box
        for index, col in enumerate(colors):
            pygame.draw.circle(self.screen, col, (x + LIGHT_BOX_WIDTH // 2, y + LIGHT_SPACING + index * (LIGHT_SIZE + LIGHT_SPACING) 
                                                  + LIGHT_SIZE // 2), LIGHT_SIZE // 2)

    def draw_car(self, car):
        pygame.draw.circle(self.screen, RED, (car.x, car.y), car.radius)

    def create_car(self):
        direction = random.choice(DIRECTIONS)
        match direction:
            case 0:
                return veh(0, HEIGHT // 2 + LANE_WIDTH // 2, direction)
            case 1:
                return veh(WIDTH // 2 + LANE_WIDTH // 2, HEIGHT, direction)
            case 2:
                return veh(WIDTH, HEIGHT // 2 - LANE_WIDTH // 2, direction)
            case 3:
                return veh(WIDTH // 2 - LANE_WIDTH // 2, 0, direction)

    def toggle_light(self, direction):
        current_state = self.traffic_lights[direction]
        if current_state == "green":
            self.traffic_lights[direction] = "red"
        else:
            self.traffic_lights[direction] = "green"

    def check_traffic(self):
        stop_offset = 100
        for car in self.cars:
            match car.direction:
                case 0:
                    if not car.passed_intersection and self.traffic_lights["left"] == "red" and WIDTH//2 + ROAD_WIDTH//2 - stop_offset <= car.x + car.radius <= WIDTH//2 + ROAD_WIDTH//2:
                        car.speed = 0
                    else:
                        car.speed = 1
                        if car.x >= WIDTH // 2 + ROAD_WIDTH//2 - stop_offset:
                            car.passed_intersection = True
                case 1:
                    if not car.passed_intersection and self.traffic_lights["bottom"] == "red" and HEIGHT//2 + ROAD_WIDTH//2 - stop_offset <= car.y - car.radius <= HEIGHT//2 + ROAD_WIDTH//2:
                        car.speed = 0
                    else:
                        car.speed = 1
                        if car.y <= HEIGHT // 2 + ROAD_WIDTH//2:
                            car.passed_intersection = True
                case 2:
                    if not car.passed_intersection and self.traffic_lights["right"] == "red" and WIDTH//2 - LIGHT_BOX_HEIGHT//2 + stop_offset >= car.x - car.radius >= WIDTH//2:
                        car.speed = 0
                    else:
                        car.speed = 1
                        if car.x <= WIDTH // 2 - LIGHT_BOX_HEIGHT//2 + stop_offset:
                            car.passed_intersection = True
                case 3:
                    if not car.passed_intersection and self.traffic_lights["top"] == "red" and HEIGHT//2 - LIGHT_BOX_HEIGHT//2 + stop_offset >= car.y + car.radius > HEIGHT//2 - ROAD_WIDTH//2:
                        car.speed = 0
                    else:
                        car.speed = 1
                        if car.y >= HEIGHT // 2 - ROAD_WIDTH//2:
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

    def reset(self):
        self.cars = []
        self.traffic_lights = {
        "top": "green",
        "bottom": "green",
        "left": "green",
        "right": "green"
        }

    def check_car_out_of_bounds(self, car):
        out_left = car.direction == 0 and car.x > WIDTH
        out_bottom = car.direction == 1 and car.y < 0
        out_right = car.direction == 2 and car.x < 0
        out_top = car.direction == 3 and car.y > HEIGHT
        return out_left or out_right or out_bottom or out_top


    def update_simulation(self):
        for car in self.cars:
            self.check_traffic()
            car.move(self.cars)
            #self.draw_car(car)

        current_time = time.time()
        if current_time - self.last_creation_time >= 0.1:
            self.cars.append(self.create_car())
            self.last_creation_time = time.time()

        self.cars = [car for car in self.cars if not self.check_car_out_of_bounds(car)]

    def render(self, episode_number):
        self.screen.fill(BLACK)

        self.draw_roads()
        self.draw_traffic_light(WIDTH//2 - ROAD_WIDTH//2 - LIGHT_BOX_WIDTH - 10, HEIGHT//2 - LIGHT_BOX_HEIGHT//2, self.traffic_lights["left"])
        self.draw_traffic_light(WIDTH//2 + ROAD_WIDTH//2 + 10, HEIGHT//2 - LIGHT_BOX_HEIGHT//2, self.traffic_lights["right"])
        self.draw_traffic_light(WIDTH//2 - LIGHT_BOX_WIDTH//2, HEIGHT//2 - ROAD_WIDTH//2 - LIGHT_BOX_HEIGHT - 10, self.traffic_lights["top"])
        self.draw_traffic_light(WIDTH//2 - LIGHT_BOX_WIDTH//2, HEIGHT//2 + ROAD_WIDTH//2 + 10, self.traffic_lights["bottom"])

        # Render episode number
        text_surface = self.font.render(f"Episode: {episode_number}", True, WHITE)
        text_rect = text_surface.get_rect(topright=(WIDTH - 10, 10))
        self.screen.blit(text_surface, text_rect)

        for car in self.cars:
            self.draw_car(car)
        pygame.display.flip()

class TrafficSimEnv(gym.Env):
    def __init__(self, trafficsim):
        super(TrafficSimEnv, self).__init__()
        self.trafficsim = trafficsim
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(6,), dtype=int)
        self.episode_number = 0

        self.state = self.get_state()

    def get_state(self):
        num_cars_top = len([car for car in self.trafficsim.cars if car.direction in [3] and not car.passed_intersection])
        num_cars_bottom = len([car for car in self.trafficsim.cars if car.direction in [1] and not car.passed_intersection])
        num_cars_left = len([car for car in self.trafficsim.cars if car.direction in [0] and not car.passed_intersection])
        num_cars_right = len([car for car in self.trafficsim.cars if car.direction in [2] and not car.passed_intersection])
        total_waiting_time = sum(car.waiting_time for car in self.trafficsim.cars)
        light_states = sum(1 << i for i, light in enumerate(self.trafficsim.traffic_lights.values()) if light == "green")
        return np.array([num_cars_top, num_cars_bottom, num_cars_left,  num_cars_right, total_waiting_time, light_states])

    def step(self, action):
        done = False
        terminated = False
        info = {}
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Decode action into traffic light states
        self.trafficsim.traffic_lights["top"] = "green" if action & 1 else "red"
        self.trafficsim.traffic_lights["bottom"] = "green" if action & 1 else "red"
        self.trafficsim.traffic_lights["left"] = "green" if action & 2 else "red"
        self.trafficsim.traffic_lights["right"] = "green" if action & 2 else "red"

        # Run simulation step
        previous_state = self.state.copy()
        self.trafficsim.update_simulation()
        self.trafficsim.render(self.episode_number)
        self.state = self.get_state()

        reward = 0

        # Calculate reward
        #waiting_time_decreased = previous_state[4] - self.state[4]
        #cars_moved = self.state[0]+ self.state[1] + self.state[2] + self.state[3] - len(self.trafficsim.cars)
        #reward = 10 * cars_moved + 0.1 * waiting_time_decreased 

        collision_occured = self.trafficsim.check_collision()
        #Check if episode is done


        if collision_occured:
            reward -= 30

        LONG_QUEUE_THRESHOLD = 20
        queue_lengths = [self.state[i] for i in range(4)]

        for queue_length in queue_lengths:
            if queue_length > LONG_QUEUE_THRESHOLD:
                reward -= 50

        #reward -= (self.state[0] + self.state[1] + self.state[2] + self.state[3]) * 2  # Penalize based on current queue length, adjust multiplier as needed

        reward -= 1

        if collision_occured or elapsed_time > 20:
            done = True
            terminated = True
            info['reason'] = 'collision'
            self.reset()
        else:
            done = False
            terminated = False

        return self.state, float(reward), done, terminated, info

    def reset(self, **kwargs):
        seed = kwargs.get('seed', None)
        if seed is not None:
            np.random.seed(seed)
        self.start_time = time.time()
        self.trafficsim.reset()  # Reset the traffic simulation
        self.state = self.get_state()  # Get initial state
        self.episode_number += 1
        info = {}

        return self.state, info     


if __name__ == "__main__":
    sim = trafficsim()
    env = TrafficSimEnv(sim)

    check_env(env, warn=True)

    model = PPO("MlpPolicy", env, verbose=1)
    
    iteration = 0
    while True:  # Replace this with a condition to stop training if needed
        print(f"Starting training iteration: {iteration}")
        model.learn(total_timesteps=1000)  # Smaller increments
        
        # Optional: Evaluate the model every N iterations
        if iteration % 10 == 0:
            mean_reward, std_reward = evaluate_policy(model.policy, model.get_env(), n_eval_episodes=10)
            print(f"Iteration: {iteration}, Mean reward: {mean_reward} +/- {std_reward}")
            # Implement any condition to adjust the training based on performance
        
        # Save the model periodically
        if iteration % 50 == 0:
            model.save(f"ppo_traffic_sim_{iteration}.zip")
        
        iteration += 1


"""
if __name__ == "__main__":
    sim = trafficsim()
    env = TrafficSimEnv(sim)


    check_env(env, warn=True)

    model = PPO("MlpPolicy", env, verbose=1)

    total_iterations = 10  # Or however many iterations you want to run

    model.learn(total_timesteps=1000000)

    mean_reward, std_reward = evaluate_policy(model.policy, model.get_env(), n_eval_episodes=10)
    #print(f"Mean reward: {mean_reward} +/- {std_reward}")

    #obs, info = env.reset()
    #for _ in range(1000):
    #    action, _states = model.predict(obs, deterministic=True)
    #    obs, rewards, done, terminated, info = env.step(action)
    #    #env.render()
    #    if done:
    #        break"""