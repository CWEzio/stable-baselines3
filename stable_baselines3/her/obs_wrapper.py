from typing import Tuple, Union

import numpy as np
from gym import spaces

from stable_baselines3.common.vec_env import VecEnv, VecEnvWrapper


class ObsWrapper(VecEnvWrapper):
    """
    Wrapper for a VecEnv which overrides the observation space for Hindsight Experience Replay to support dict observations.

    :param env: (VecEnv) The vectorized environment to wrap.
    """

    def __init__(self, venv: VecEnv):
        super(ObsWrapper, self).__init__(venv, venv.observation_space, venv.action_space)

        self.venv = venv

        self.spaces = list(venv.observation_space.spaces.values())

        # get dimensions of observation and goal
        if isinstance(self.spaces[0], spaces.Discrete):
            self.obs_dim = 1
            self.goal_dim = 1
        else:
            self.obs_dim = venv.observation_space.spaces["observation"].shape[0]
            self.goal_dim = venv.observation_space.spaces["achieved_goal"].shape[0]

        # new observation space with concatenated observation and (desired) goal
        # for the different types of spaces
        if isinstance(self.spaces[0], spaces.Box):
            low_values = np.concatenate(
                [venv.observation_space.spaces["observation"].low, venv.observation_space.spaces["desired_goal"].low]
            )
            high_values = np.concatenate(
                [venv.observation_space.spaces["observation"].high, venv.observation_space.spaces["desired_goal"].high]
            )
            self.observation_space = spaces.Box(low_values, high_values, dtype=np.float32)
        elif isinstance(self.spaces[0], spaces.MultiBinary):
            total_dim = self.obs_dim + self.goal_dim
            self.observation_space = spaces.MultiBinary(total_dim)
        elif isinstance(self.spaces[0], spaces.Discrete):
            dimensions = [venv.observation_space.spaces["observation"].n, venv.observation_space.spaces["desired_goal"].n]
            self.observation_space = spaces.MultiDiscrete(dimensions)
        else:
            raise NotImplementedError(f"{type(self.spaces[0])} space is not supported")

    def reset(self) -> Union[int, float]:
        return self.venv.reset()

    def step_wait(self) -> Tuple[Union[int, float], float, bool, dict]:
        return self.venv.step_wait()
