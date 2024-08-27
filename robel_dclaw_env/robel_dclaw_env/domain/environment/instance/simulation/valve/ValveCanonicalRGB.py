from pprint import pprint
from robel_dclaw_env.domain.environment.instance.simulation.base_environment import RobotCanonicalRGB


class ValveCanonicalRGB:
    def __init__(self):
       self.robot_canonical_rgb = RobotCanonicalRGB()

    def get_rgb_dict(self, object_rgb_dict):
        return {
            **self.robot_canonical_rgb.get_rgb_dict(),
            **self.__object(object_rgb_dict)
        }

    def __object(self, object_rgb_list: list):
        return {
            # ------ valve ------
            "vis_valve_3fin_handle_1"   : object_rgb_list[0],
            "vis_valve_3fin_handle_2"   : object_rgb_list[1],
            "vis_valve_3fin_handle_3"   : object_rgb_list[2],
            "vis_valve_3fin_center"     : object_rgb_list[3],
        }

if __name__ == '__main__':

    object_rgb_dict = [
        [255, 0, 0], # red
        [0, 255, 0], # green
        [0, 0, 255], # blue
    ]

    can = ValveCanonicalRGB()
    pprint(can.get_rgb_dict(object_rgb_dict))
