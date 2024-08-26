from pprint import pprint
from robel_dclaw_env.domain.environment.instance.simulation.base_environment import RobotCanonicalRGB


class ValveCanonicalRGB:
    def __init__(self):
       self.robot_canonical_rgb = RobotCanonicalRGB()

    def get_rgb_dict(self, object_rgb):
        return {
            **self.robot_canonical_rgb.get_rgb_dict(),
            **self.__object(object_rgb)
        }

    def __object(self, object_rgb: list):
        return {
            # ------ valve ------
            "vis_valve_3fin_handle_1"   : object_rgb,
            "vis_valve_3fin_handle_2"   : object_rgb,
            "vis_valve_3fin_handle_3"   : object_rgb,
            "vis_valve_3fin_center"     : object_rgb,
        }


if __name__ == '__main__':

    object_rgb = [255, 0, 255]

    can = ValveCanonicalRGB()
    pprint(can.get_rgb_dict(object_rgb))
