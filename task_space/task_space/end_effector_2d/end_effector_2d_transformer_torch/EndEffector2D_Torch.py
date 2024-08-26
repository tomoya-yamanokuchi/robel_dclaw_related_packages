from argparse import Action
import sys
import pathlib
import copy
import torch
from matplotlib import axes
from matplotlib.pyplot import axis
import numpy as np
from numpy.core.defchararray import index, join

import sys; import pathlib; p = pathlib.Path(); sys.path.append(str(p.cwd()))
from robel_dclaw_env.custom_service import angle_interface as ai

from robel_dclaw_env.custom_service import normalize, NTD
from ..end_effector_2d_value_object import TaskSpacePosition_2D_Plane
from ..end_effector_2d_value_object import BiasedEndEffectorPosition_2D_Plane
from robel_dclaw_env.domain.environment.instance.simulation.base_environment import EndEffectorPosition
import sys; import pathlib; p = pathlib.Path(); sys.path.append(str(p.cwd()))
from robel_dclaw_env.domain.environment.kinematics import ForwardKinematics, InverseKinematics
from task_space import AbstractTaskSpaceTransformer


class EndEffector2D_Torch(AbstractTaskSpaceTransformer):
    def __init__(self):
        self.num_claw                = 3
        self._inverse_kinematics     = ForwardKinematics()
        self._forward_kinematics     = InverseKinematics()


    def denormalize(self, x_norm, x_min, x_max, m, M):
        return ((x_norm - m) / (M - m)) * (x_max - x_min) + x_min


    def _task2end_1claw(self, task_space_position):
        z_task         = task_space_position[:, :, 0] # 順番間違えないように！
        y_task         = task_space_position[:, :, 1] # 順番間違えないように！
        y_end_effector = self.denormalize(y_task, x_min=BiasedEndEffectorPosition_2D_Plane.y_lb, x_max=BiasedEndEffectorPosition_2D_Plane.y_ub, m=TaskSpacePosition_2D_Plane._min, M=TaskSpacePosition_2D_Plane._max)
        z_end_effector = self.denormalize(z_task, x_min=BiasedEndEffectorPosition_2D_Plane.z_lb, x_max=BiasedEndEffectorPosition_2D_Plane.z_ub, m=TaskSpacePosition_2D_Plane._min, M=TaskSpacePosition_2D_Plane._max)
        x_end_effector = torch.zeros(y_end_effector.shape).cuda() + BiasedEndEffectorPosition_2D_Plane.x_base
        return torch.stack([x_end_effector, y_end_effector, z_end_effector], dim=-1)


    # @abstractmethod
    def task2end(self, task_space_position: TaskSpacePosition_2D_Plane):
        # import ipdb; ipdb.set_trace()
        dim_task_space_for_each_claw = 2
        end_effector_position = [self._task2end_1claw(x) for x in torch.split(task_space_position.tensor_value, dim_task_space_for_each_claw, dim=-1)]
        return EndEffectorPosition(torch.cat(end_effector_position, dim=-1))


    # @abstractmethod
    def end2task(self, end_effector_position: EndEffectorPosition):
        # import ipdb; ipdb.set_trace()
        dim_end_effector_position_for_each_claw = 3
        task_space_position = [self._end2task_1claw(x) for x in torch.split(end_effector_position.value, dim_end_effector_position_for_each_claw, dim=-1)]
        return TaskSpacePosition_2D_Plane(torch.cat(task_space_position, dim=-1))



    def _end2task_1claw(self, end_effector_position_1claw):
        y      = end_effector_position_1claw[:, :, 1]
        z      = end_effector_position_1claw[:, :, 2]
        y_task = normalize(x=y, x_min=BiasedEndEffectorPosition_2D_Plane.y_lb, x_max=BiasedEndEffectorPosition_2D_Plane.y_ub, m=TaskSpacePosition_2D_Plane._min, M=TaskSpacePosition_2D_Plane._max)
        z_task = normalize(x=z, x_min=BiasedEndEffectorPosition_2D_Plane.z_lb, x_max=BiasedEndEffectorPosition_2D_Plane.z_ub, m=TaskSpacePosition_2D_Plane._min, M=TaskSpacePosition_2D_Plane._max)
        return torch.stack([z_task, y_task], dim=-1) # np.c_[z, y] # 順番間違えないように！

