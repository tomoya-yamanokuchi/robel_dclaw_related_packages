import copy
from icem_mpc.multiprocessing.ForkedPdb import ForkedPdb




def forward_model_with_fixed_initial_point(state, action):


    ForkedPdb().set_trace()

    assert len(action.shape) == 3 # (num_sample, horizon, dim)
    assert action.shape[-1]  == 2
    action = copy.deepcopy(action)
    action[:, 0, 0] = state[0]
    action[:, 0, 1] = state[1]
    return action

