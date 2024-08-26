import numpy as np
from .object_state.ValvePosition import ValvePosition
from .object_state.ValveVelocity import ValveVelocity
from robel_dclaw_env.domain.environment.instance.simulation.base_environment.state.MjSimTime import MjSimTime
from robel_dclaw_env.domain.environment.instance.simulation.base_environment.state.MjSimAct import MjSimAct
from robel_dclaw_env.domain.environment.instance.simulation.base_environment.state.MjSimUddState import MjSimUddState
from robel_dclaw_env.domain.environment.instance.simulation.base_environment.state.RobotPosition import RobotPosition
from robel_dclaw_env.domain.environment.instance.simulation.base_environment.state.RobotVelocity import RobotVelocity
from robel_dclaw_env.domain.environment.kinematics import EndEffectorPosition
from robel_dclaw_env.custom_service import NTD
from task_space import TaskSpaceBuilder
from torch_numpy_converter import to_tensor

# task_space = TaskSpaceBuilder().build(env_name="sim_valve", mode="torch")


StateValueObject = {
    "task_space_position"   : object, # task_space["TaskSpacePosition"],
    "end_effector_position" : EndEffectorPosition,
    "robot_position"        : RobotPosition,
    "robot_velocity"        : RobotVelocity,
    "object_position"       : ValvePosition,
    "object_velocity"       : ValveVelocity,
    "time"                  : MjSimTime,
    "act"                   : MjSimAct,
    "udd_state"             : MjSimUddState,
}

debug = True


class ValveState:
    def __init__(self, **kwargs: dict):
        self.collection = {}
        for key, val in kwargs.items():
            if debug: print("key, val, val_shape = {}, {}".format(key, val))
            state_value_object = StateValueObject[key]

            if (key != "time") and (key != "act") and (key != "udd_state"):
                val = to_tensor(np.array(val))
            if key == "udd_state":
                val = dict()

            if key == "task_space_position": val = NTD(val)
            self.collection[key] = state_value_object(val)


            if key == "time"                : self.collection[key] = state_value_object(val)
            if key == "act"                 : self.collection[key] = state_value_object(val)
            if key == "udd_state"           : self.collection[key] = state_value_object(val)
            if key == "task_space_position" : self.collection[key] = state_value_object(NTD(val))

            i
