from magent2.environments import battle_v4
import os
import cv2
from dqn_model import DQN
import torch
import random


if __name__ == "__main__":
    env = battle_v4.env(map_size=45, render_mode="rgb_array")
    vid_dir = "video"
    os.makedirs(vid_dir, exist_ok=True)
    fps = 35
    frames = []

    def policy(observation, q_network):
        sample = random.random()
        if sample < 0.1:
            return env.action_space("blue_0").sample()
        else:
            observation = torch.Tensor(observation).to("cuda")
            with torch.no_grad():
                q_values = q_network(observation)
            return torch.argmax(q_values, dim=1).cpu().numpy()[0]
    
    q_network_blue = DQN(
        env.observation_space("red_0").shape, env.action_space("red_0").n
    ).to("cuda")
    q_network_blue.load_state_dict(
        torch.load("models/blue_17.pt", weights_only=True, map_location="cpu")["policy_net_state_dict"]
    )

    #random policies
    env.reset()
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None  # this agent has died
        else:
            agent_handle = agent.split("_")[0]
            if agent_handle == "red":
                action = env.action_space(agent).sample()
            elif agent_handle == "blue":
                action =   policy(observation, q_network_blue)

        env.step(action)

        if agent == "blue_0":
            frames.append(env.render())

    height, width, _ = frames[0].shape
    out = cv2.VideoWriter(
        os.path.join(vid_dir, f"random.mp4"),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    for frame in frames:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    out.release()
    print("Done recording random agents")

    # pretrained policies
    frames = []
    env.reset()
    from torch_model import QNetwork
    import torch

    q_network = QNetwork(
        env.observation_space("red_0").shape, env.action_space("red_0").n
    )
    q_network.load_state_dict(
        torch.load("red.pt", weights_only=True, map_location="cpu")
    )
    for agent in env.agent_iter():

        observation, reward, termination, truncation, info = env.last()
        
        if termination or truncation:
            action = None  # this agent has died
        else:
            agent_handle = agent.split("_")[0]
            if agent_handle == "red":
                observation = (
                    torch.Tensor(observation).float().permute([2, 0, 1]).unsqueeze(0)
                )
                with torch.no_grad():
                    q_values = q_network(observation)
                action = torch.argmax(q_values, dim=1).numpy()[0]
            else:
                action =   policy(observation, q_network_blue)

        env.step(action)

        if agent == "blue_0":
            frames.append(env.render())

    height, width, _ = frames[0].shape
    out = cv2.VideoWriter(
        os.path.join(vid_dir, f"pretrained.mp4"),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    for frame in frames:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    out.release()
    print("Done recording pretrained agents")
    
    # trained models 
    frames = []
    env.reset()
    from final_torch_model import QNetwork as FinalQNetwork
    import torch

    q_network = FinalQNetwork(
        env.observation_space("red_0").shape, env.action_space("red_0").n
    )
    q_network.load_state_dict(
        torch.load("red_final.pt", weights_only=True, map_location="cpu")
    )
    for agent in env.agent_iter():

        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None  # this agent has died
        else:
            agent_handle = agent.split("_")[0]
            if agent_handle == "red":
                observation = (
                    torch.Tensor(observation).float().permute([2, 0, 1]).unsqueeze(0)
                )
                with torch.no_grad():
                    q_values = q_network(observation)
                action = torch.argmax(q_values, dim=1).numpy()[0]
            else:
                action =   policy(observation, q_network_blue)

        env.step(action)

        if agent == "blue_0":
            frames.append(env.render())

    height, width, _ = frames[0].shape
    out = cv2.VideoWriter(
        os.path.join(vid_dir, f"trained.mp4"),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    for frame in frames:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    out.release()
    print("Done recording trained agents")

    env.close()
