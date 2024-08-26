from domain_object_builder import DomainObject
from domain_object_builder import DomainObjectBuilder
from domain_object_director import CheckEnvRolloutDirector
from usecase.xml_generation.pushing_object_xml_generation import pushing_object_xml_generation
from service import NTD
import numpy as np


class CheckEnvDataset:
    @staticmethod
    def run(domain_object: DomainObject,  radius_list: list):
        env                      = domain_object.env
        init_state               = domain_object.init_state
        TaskSpaceValueObject     = domain_object.TaskSpaceValueObject
        TaskSpaceDiffValueObject = domain_object.TaskSpaceDiffValueObject
        config_xml               = domain_object.config_xml_generation
        # ---
        xml_path                 = domain_object.original_xml_path
        task_space_position_init = init_state["task_space_position"]

        for i in range(5):
            pushing_object_xml_generation(config_xml, radius=radius_list[i])
            # ---
            env.set_xml_path(xml_path)
            env.load_model()
            env.reset(init_state)

            # for k in range(5):
            env.set_task_space_ctrl(task_space_position_init)
            env.step(is_view=True)

            env.render()
            # import ipdb; ipdb.set_trace()
            for t in range(5):
                render = env.render()    # ; print(render)
                state  = env.get_state() # ; print(state)
                env.view()
                # ---
                ud                   = np.zeros_like(task_space_position_init.value)
                ud[:, :, 1:2:2]     += 0.15
                task_space_diff_ctrl = TaskSpaceDiffValueObject(ud)
                task_space_ctrl      = state["task_space_position"] + task_space_diff_ctrl
                ctrl                 = env.set_task_space_ctrl(task_space_ctrl)
                print("step t = {} : ctrl = {}".format(t, task_space_ctrl.value.squeeze()))
                # ----
                env.step(is_view=True)
                # import ipdb; ipdb.set_trace()

if __name__ == '__main__':
    radius_list = [
        0.008,
        0.012,
        0.016,
        0.020,
    ]

    # # --- test ---
    # radius_list = [
    #     0.006,
    #     0.010,
    #     0.014,
    #     0.018,
    #     0.022,
    # ]

    builder       = DomainObjectBuilder()
    director      = CheckEnvRolloutDirector()
    domain_object = director.construct(builder, env_name="sim/pushing")
    CheckEnvDataset.run(domain_object, radius_list)
