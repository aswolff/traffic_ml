import os
from rlagent import *
from traffic_sim import TrafficSim

def main():
    sim = TrafficSim()
    env = Rlagent(sim)

    model = PPO("MlpPolicy", env, verbose=1)
    obs, info = env.reset()

    should_exit = False

    while not should_exit:
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, done, terminated, info = env.step(action)
        should_exit = sim.process_events()

        if done:
            obs, info = env.reset()

    # Ensure the models directory exists
    model_save_dir = "../models"
    if not os.path.exists(model_save_dir):
        os.makedirs(model_save_dir)

    # Save the model
    model_save_path = os.path.join(model_save_dir, "traffic_agent")
    model.save(model_save_path)

    pygame.quit()
        
if __name__ == "__main__":
    main()