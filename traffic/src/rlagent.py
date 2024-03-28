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
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(13,), dtype=int)
        self.episode_number = 0
        self.waiting_time_penalty = 10
        self.collision_penalty = 100

        self.state = self.get_state()

    def get_state(self):
        num_cars_top = len([car for car in self.trafficsim.cars if car.direction in [3] and not car.passed_intersection])
        num_cars_bottom = len([car for car in self.trafficsim.cars if car.direction in [1] and not car.passed_intersection])
        num_cars_left = len([car for car in self.trafficsim.cars if car.direction in [0] and not car.passed_intersection])
        num_cars_right = len([car for car in self.trafficsim.cars if car.direction in [2] and not car.passed_intersection])
        total_waiting_time = sum(car.waiting_time for car in self.trafficsim.cars)
        light_toggle_times = np.array(list(self.trafficsim.last_toggle_time.values()))
        light_states = np.array(list(self.trafficsim.traffic_lights.values()))

        state = np.concatenate(([num_cars_top, num_cars_bottom, num_cars_left, num_cars_right, total_waiting_time], light_toggle_times, light_states))

        return state

        #return np.array([num_cars_top, num_cars_bottom, num_cars_left, num_cars_right, total_waiting_time, light_states])
    
    def step(self, action: int):
        done = False
        terminated = False
        info = {}
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Handling actions
        if action == 0:
            self.trafficsim.toggle_light("top")
        elif action == 1:
            self.trafficsim.toggle_light("bottom")
        elif action == 2:
            self.trafficsim.toggle_light("left")
        elif action == 3:
            self.trafficsim.toggle_light("right")
        elif action == 4:
            # Do nothing
            pass


        # Run simulation step
        previos_state = self.state.copy()
        self.trafficsim.update_simulation()
        self.trafficsim.render(self.episode_number)
        self.state = self.get_state()

        reward = 0

        # Check for collision or cars waiting
        collision_occured = self.trafficsim.check_collision()
        waiting_time = sum(car.waiting_time for car in self.trafficsim.cars)

        if collision_occured:
            reward -= self.collision_penalty
        
        reward -= waiting_time * self.waiting_time_penalty

        reward -= 1

        if collision_occured or elapsed_time > 20:
            #done = True
            #terminated = True
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