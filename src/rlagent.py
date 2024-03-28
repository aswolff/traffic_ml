import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
from traffic_sim import *

class Rlagent(gym.Env):
    def __init__(self, trafficsim: TrafficSim):
        super(Rlagent, self).__init__()
        self.trafficsim = trafficsim
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(6,), dtype=int)
        self.episode_number = 0
        self.waiting_time_penalty = 50
        self.collision_penalty = 30

        self.state = self.get_state()

    def get_state(self):
        num_cars_top = len([car for car in self.trafficsim.cars if car.direction in [3] and not car.passed_intersection])
        num_cars_bottom = len([car for car in self.trafficsim.cars if car.direction in [1] and not car.passed_intersection])
        num_cars_left = len([car for car in self.trafficsim.cars if car.direction in [0] and not car.passed_intersection])
        num_cars_right = len([car for car in self.trafficsim.cars if car.direction in [2] and not car.passed_intersection])
        total_waiting_time = sum(car.waiting_time for car in self.trafficsim.cars)
        light_states = sum(1 << i for i, light in enumerate(self.trafficsim.traffic_lights.values()) if light == 1)
        return np.array([num_cars_top, num_cars_bottom, num_cars_left,  num_cars_right, total_waiting_time, light_states])

    
    def step(self, action: int):
        done = False
        terminated = False
        info = {}
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        reward = 0

        # Handling actions
        self.trafficsim.traffic_lights["top"] = 1 if action & 1 else 0
        self.trafficsim.traffic_lights["bottom"] = 1 if action & 1 else 0
        self.trafficsim.traffic_lights["left"] = 1 if action & 2 else 0
        self.trafficsim.traffic_lights["right"] = 1 if action & 2 else 0

        # Run simulation step
        self.trafficsim.update_simulation()
        self.trafficsim.render(self.episode_number)
        self.state = self.get_state()

        # Check for collision or cars waiting
        collision_occured = self.trafficsim.check_collision()

        if collision_occured:
            reward -= self.collision_penalty

        LONG_QUEUE_THRESHOLD = 20
        queue_lengths = [self.state[i] for i in range(4)]

        for queue_length in queue_lengths:
            if queue_length > LONG_QUEUE_THRESHOLD:
                reward -= self.waiting_time_penalty
        
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
        self.trafficsim.reset()
        self.state = self.get_state()
        self.episode_number += 1
        info = {}

        return self.state, info