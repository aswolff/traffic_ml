# Traffic-Mind
# Traffic Light Simulation with Reinforcement Learning

This project is a simulation of traffic flow at an intersection, controlled by traffic lights whose states are determined through reinforcement learning (RL). The simulation is built using Python, leveraging libraries such as Pygame for visualization and Stable Baselines3 for implementing the RL agent.

## Features

- **Dynamic Traffic Simulation**: Generates cars approaching an intersection from four directions, simulating real-world traffic flow.
- **Reinforcement Learning Agent**: Utilizes the Proximal Policy Optimization (PPO) algorithm from Stable Baselines3 to optimize traffic light control for minimizing waiting times and avoiding traffic congestion.
- **Customizable Environment**: The simulation parameters, such as traffic frequency and light switching logic, can be adjusted to explore different traffic management strategies.
- **Visualization**: Built with Pygame, the simulation provides a graphical representation of the traffic flow and the state of traffic lights at the intersection.

## Getting Started

### Prerequisites

Before you run the simulation, ensure you have the following installed:

- Python 3.7 or later
- Pygame
- NumPy
- Gymnasium
- Stable Baselines3

You can install the required libraries using pip:
- pip install pygame numpy gymnasium stable-baselines3

### Running the Simulation
To start the simulation, run the traffic.py script:
python traffic.py

### Customization
You can customize the simulation by modifying parameters in the traffic.py file, such as the car generation rate, traffic light switching logic, and more, to explore different traffic management strategies.

### Reinforcement Learning Model
This project uses the Proximal Policy Optimization (PPO) algorithm for training the traffic light control agent. The model aims to learn an optimal policy for switching traffic lights to improve traffic flow and reduce waiting times.
