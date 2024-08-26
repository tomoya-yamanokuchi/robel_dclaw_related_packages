import mujoco_py
# ----- general module -----
from ....kinematics import NumpyForwardKinematics
from ....kinematics import NumpyInverseKinematics
from ..base_environment import AbstractEnvironment, BaseEnvironment, ModelLoader
from ..base_environment import SetState, GetState, StateDict
from ..base_environment import SetCtrl, CtrlDict
from ..base_environment import RenderingManager
from ..base_environment.viewer.ViewerFactory import ViewerFactory
from ..base_environment.dynamics_parameter import RobotDynamicsParameter
from ..base_environment.joint_range import RobotJointRange
from ..base_environment.ctrl_range import RobotCtrlRange
from task_space import TaskSpaceFactory
# ----- Env Specific ---
from .ValveDyanmicsParameter import ValveDyanmicsParameter
from .ValveJointRange import ValveJointRange
from .ValveTarget import ValveTarget
from .ValveStateFactory import ValveStateFactory
from task_space.manifold_1d import TaskSpacePositionValue_1D_Manifold
from .ValveCanonicalRGB import ValveCanonicalRGB


class ValveSimulationEnvironment(AbstractEnvironment):
    def __init__(self, config, use_render=True):
        self.env_name               = "sim_valve"
        self.canonical_rgb_manager  = ValveCanonicalRGB()
        # ----
        self.base_env               = BaseEnvironment(config)
        self.model_loader           = ModelLoader(self.base_env, config)
        self.forward_kinematics     = NumpyForwardKinematics()
        self.inverse_kinematics     = NumpyInverseKinematics()
        self.config                 = config
        self.use_render             = use_render

        self.task_space_transformer = TaskSpaceFactory.create_transformer(self.env_name, mode="numpy")
        self.TaskSpaceValueObject   = TaskSpaceFactory.create_position(self.env_name)
        # ----
        self.viewer    = None
        self.rendering = None


    def model_file_reset(self):
        self.model         = self.model_loader.load()
        self.canonical_rgb = self.canonical_rgb_manager.get_rgb_dict(self.config.xml.rgb.object)

    def set_object_rgb(self, object_rgb: list):
        self.canonical_rgb = self.canonical_rgb_manager.get_rgb_dict(object_rgb)
        self.rendering.set_canonical_rgb(self.canonical_rgb.rgb)

    def reset(self, state, verbose=False):
        if self.base_env.sim is None:
            self.model_file_reset()
            self.base_env.sim      = mujoco_py.MjSim(self.model)
            self.setState          = SetState(self.base_env.sim, self.task_space_transformer)
            self.getState          = GetState(self.base_env.sim, ValveStateFactory, self.task_space_transformer)
            self.setCtrl           = SetCtrl(self.base_env, self.task_space_transformer)
            self.setTargetPosition = ValveTarget(self.base_env.sim)
            self.setTargetPosition.set_target_visible(self.config.target.visible)
            RobotDynamicsParameter(self.base_env.sim).set(self.config.dynamics.robot)
            ValveDyanmicsParameter(self.base_env.sim).set(self.config.dynamics.object)
            RobotJointRange(self.base_env.sim).set_range(**self.config.joint_range.robot)
            ValveJointRange(self.base_env.sim).set_range(**self.config.joint_range.object)
            RobotCtrlRange(self.base_env.sim).set_range()
            self._initialize_viewer_and_render()
        self.base_env.sim.reset()
        self.set_state(state)
        if self.use_render:
            self.rendering.register_new_randomized_texture_collection()
        # print(self.base_env.sim.get_state().time)
        self.base_env.sim.step()
        if verbose: print("\n <---- reset --->\n")


    def _initialize_viewer_and_render(self):
        if not self.use_render: return
        if self.viewer is None:
            self.viewer = ViewerFactory().create(self.config.viewer.is_Offscreen)(self.base_env.sim)
        if self.rendering is None:
            self.rendering = RenderingManager(
                sim            = self.base_env.sim,
                canonical_rgb  = self.canonical_rgb,
                config_render  = self.config.render,
                config_texture = self.config.texture,
                config_camera  = self.config.camera,
                config_light   = self.config.light,
            )

    def render(self):
        assert self.viewer is not None # to be initialized before rendering
        assert self.rendering is not None
        self.image = self.rendering.render()
        return self.image

    def view(self):
        self.viewer.view(self.image)

    def get_state(self) -> StateDict:
        return self.getState.get_state()

    def set_state(self, state: StateDict):
        self.setState.set_state(state)

    def set_task_space_ctrl(self, TaskSpacePosition: TaskSpacePositionValue_1D_Manifold) -> CtrlDict:
        return self.setCtrl.set_ctrl(TaskSpacePosition)

    def set_joint_space_ctrl(self, joint_space_position):
        return self.setCtrl.set_joint_space_ctrl(joint_space_position)

    def set_target_position(self, target_position):
        self.setTargetPosition.set_target_position(target_position)

    def step(self, is_view=False):
        self.base_env.step(is_view)
