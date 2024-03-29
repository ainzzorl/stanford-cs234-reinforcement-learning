import torch
import torch.nn as nn
import torch.nn.functional as F
import copy

from utils.general import get_logger
from utils.test_env import EnvTest
from q4_schedule import LinearExploration, LinearSchedule
from q5_linear_torch import Linear


from configs.q6_nature import config


class NatureQN(Linear):
    """
    Implementing DeepMind's Nature paper. Here are the relevant urls.
    https://storage.googleapis.com/deepmind-data/assets/papers/DeepMindNature14236Paper.pdf

    Model configuration can be found in the Methods section of the above paper.
    """

    def initialize_models(self):
        """Creates the 2 separate networks (Q network and Target network). The input
        to these models will be an img_height * img_width image
        with channels = n_channels * self.config.state_history

        1. Set self.q_network to be a model with num_actions as the output size
        2. Set self.target_network to be the same configuration self.q_network but initialized from scratch
        3. What is the input size of the model?

        To simplify, we specify the paddings as:
            (stride - 1) * img_height - stride + filter_size) // 2

        Hints:
            1. Simply setting self.target_network = self.q_network is incorrect.
            2. The following functions might be useful
                - nn.Sequential
                - nn.Conv2d
                - nn.ReLU
                - nn.Flatten
                - nn.Linear
        """
        state_shape = list(self.env.observation_space.shape)
        img_height, img_width, n_channels = state_shape
        num_actions = self.env.action_space.n

        ##############################################################
        ################ YOUR CODE HERE - 25-30 lines lines ################

        # stride_1 = 4
        # filter_size_1 = 8
        # padding_1 = ((stride_1 - 1) * img_height - stride_1 + filter_size_1) // 2

        # stride_2 = 2
        # filter_size_2 = 4
        # padding_2 = ((stride_2 - 1) * img_height - stride_2 + filter_size_2) // 2

        # stride_3 = 1
        # filter_size_3 = 3
        # padding_3 = ((stride_3 - 1) * img_height - stride_3 + filter_size_3) // 2

        # self.q_network = nn.Sequential(
        #     nn.Conv2d(in_channels=n_channels * self.config.state_history, out_channels=n_channels * self.config.state_history, kernel_size=filter_size_1, stride=stride_1, padding=padding_1),
        #     nn.ReLU(True),
        #     nn.Conv2d(in_channels=n_channels * self.config.state_history, out_channels=n_channels * self.config.state_history, kernel_size=filter_size_2, stride=stride_2, padding=padding_2),
        #     nn.ReLU(True),
        #     nn.Conv2d(in_channels=n_channels * self.config.state_history, out_channels=n_channels * self.config.state_history, kernel_size=filter_size_3, stride=stride_3, padding=padding_3),
        #     nn.ReLU(True),
        #     nn.Flatten(),
        #     nn.Linear(1536, num_actions),
        # )
        # self.target_network = copy.deepcopy(self.q_network)
        self.q_network = nn.Sequential(
            nn.Conv2d(in_channels=n_channels*self.config.state_history, out_channels=32, kernel_size=(8, 8), stride=(4, 4), padding=((4 - 1) * img_height - 4 + 8) // 2),
            nn.ReLU(),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(4, 4), stride=(2, 2), padding=((2 - 1) * img_height - 2 + 4) // 2),
            nn.ReLU(),
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=(3, 3), stride=(1, 1), padding=((1 - 1) * img_height - 1 + 3) // 2),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(in_features=img_height*img_width*64, out_features=512),
            nn.ReLU(),
            nn.Linear(in_features=512, out_features=num_actions)
        )
        self.target_network = copy.deepcopy(self.q_network)

        ##############################################################
        ######################## END YOUR CODE #######################

    def get_q_values(self, state, network):
        """
        Returns Q values for all actions

        Args:
            state: (torch tensor)
                shape = (batch_size, img height, img width, nchannels x config.state_history)
            network: (str)
                The name of the network, either "q_network" or "target_network"

        Returns:
            out: (torch tensor) of shape = (batch_size, num_actions)

        Hint:
            1. What are the input shapes to the network as compared to the "state" argument?
            2. You can forward a tensor through a network by simply calling it (i.e. network(tensor))
        """
        out = None

        ##############################################################
        ################ YOUR CODE HERE - 4-5 lines lines ################

        network = self.q_network if network == 'q_network' else self.target_network
        value = state.permute(0, 3, 1, 2)
        out = network(value)

        ##############################################################
        ######################## END YOUR CODE #######################
        return out


"""
Use deep Q network for test environment.
"""
if __name__ == '__main__':
    env = EnvTest((8, 8, 6))

    # exploration strategy
    exp_schedule = LinearExploration(env, config.eps_begin,
            config.eps_end, config.eps_nsteps)

    # learning rate schedule
    lr_schedule  = LinearSchedule(config.lr_begin, config.lr_end,
            config.lr_nsteps)

    # train model
    model = NatureQN(env, config)
    model.run(exp_schedule, lr_schedule)
