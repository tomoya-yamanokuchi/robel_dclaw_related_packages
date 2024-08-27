import cv2, time, copy, os
import numpy as np
from service import repeated_addition
from robel_dclaw_env.custom_service import print_info, NTD
from robel_dclaw_env.domain import EnvironmentBuilder



class EnvRolloutValve:
    @staticmethod
    def run(config):
        # --- 環境のインスタンスを生成 (*本当の実体は最初にenv.reset()が最初に実行されたタイミングで生成される) ---
        env_struct        = EnvironmentBuilder().build(config, mode="numpy")
        env               = env_struct["env"]
        init_state        = env_struct["init_state"]
        TaskSpacePosition = env_struct["TaskSpacePosition"]
        xml_path          = os.path.join(config.env.model_dir, config.env.model_file)

        # --- 制御入力を適当に作成 ---
        num_task_step            = 100
        init_task_space_position = init_state["task_space_position"].value.squeeze()
        task_space_ctrl_claw0    = repeated_addition(init_task_space_position[0], addition=0.01, num_repeat=num_task_step)
        task_space_ctrl_claw1    = repeated_addition(init_task_space_position[1], addition=0.02, num_repeat=num_task_step)
        task_space_ctrl_claw2    = repeated_addition(init_task_space_position[2], addition=0.03, num_repeat=num_task_step)
        task_space_ctrl          = np.stack([task_space_ctrl_claw0, task_space_ctrl_claw1, task_space_ctrl_claw2], axis=-1)

        # --- 環境とのインタラクションの一連のループ実行 ---
        episode = 10
        for n in range(episode):
            # ---
            env.set_xml_path(xml_path) # おまじない
            env.load_model()           # おまじない
            env.reset(init_state)      # おまじない
            env.render()
            # ---
            for t in range(num_task_step):
                render = env.render()
                state  = env.get_state()
                env.view() # [use_render=True] & [is_Offscreen=True] ならopencvのviewer画面でレンダリングされる
                # ---
                env.set_task_space_ctrl(TaskSpacePosition(NTD(task_space_ctrl[t])))
                env.step()


if __name__ == '__main__':
    import hydra
    from omegaconf import DictConfig

    @hydra.main(version_base=None, config_path="../../robel_dclaw_env/conf", config_name="config.yaml")
    def main(config: DictConfig):
        '''
        OpenCV Viewerでレンダリングするためのパラメータ設定
            1.          use_render = True
            2. viewer.is_Offscreen = True
        '''
        demo = EnvRolloutValve()
        demo.run(config)
    main()
