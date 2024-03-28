import os
from rlagent import *
from traffic_sim import TrafficSim
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.callbacks import BaseCallback
    
class TrainModel:
    def __init__(self):
        self.env = Rlagent(TrafficSim())
        self.model = PPO("MlpPolicy", self.env, verbose=1)
        self.iteration = 0
        self.check_done = False
        while not self.check_done:
            print(f'Starting training iteration: {self.iteration}')
            self.model.learn(total_timesteps=1000)

            if self.iteration % 10 == 0:
                mean_reward, std_reward = evaluate_policy(self.model.policy, self.model.get_env(), n_eval_episodes=10)
                print(f'Iteration: {self.iteration}, Mean reward: {mean_reward} +/- {std_reward}')
            
            if self.iteration % 50 == 0:
                self.save_model()

            self.check_done = self.env.trafficsim.process_events()
            self.iteration += 1

    def save_model(self):
        model_save_dir = "./models"
        if not os.path.exists(model_save_dir):
            os.makedirs(model_save_dir)
        model_save_path = os.path.join(model_save_dir, "traffic_agent")
        self.model.save(model_save_path)
