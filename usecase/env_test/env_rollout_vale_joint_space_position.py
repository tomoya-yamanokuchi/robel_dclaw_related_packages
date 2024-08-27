import cv2, time, copy, os
import numpy as np
from service import repeated_addition
import colorednoise as cn
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

        # ---
        num_task_step = 100
        episode       = 10

        # --- 相関のあるノイズからjoint_space_positionの制御入力を作成 ---
        dim_ctrl             = 9
        n_repeats            = episode     # repeat simulatons
        n_variables          = dim_ctrl    # independent variables in each simulation
        timesteps            = num_task_step # number of timesteps for each variable
        joint_space_position = cn.powerlaw_psd_gaussian(exponent=3, size=(n_repeats, n_variables, timesteps))*0.25

        # --- 環境とのインタラクションの一連のループ実行 ---
        for n in range(episode):
            # ---
            env.set_xml_path(xml_path) # おまじない
            env.load_model()           # おまじない
            env.reset(init_state)      # おまじない
            env.render()
            # ---
            for t in range(num_task_step):
                # render = env.render()
                state  = env.get_state()
                env.view()
                # ---
                env.set_joint_space_ctrl(joint_space_position[n,:,t]) # task_spaceじゃない！！
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
