import copy
import pathlib
import numpy as np
import torch
from .ReferencePosition import ReferencePosition

from ... import AbstractTaskSpaceTransformer
from ..manifold_1d_value_object import TaskSpacePositionValue_1D_Manifold as TaskSpaceValueObject
from robel_dclaw_env.domain.environment.instance.simulation.base_environment import EndEffectorPosition
from robel_dclaw_env.domain.environment.kinematics import ForwardKinematics
from .ReferenceTaskSpacefromEndEffector import ReferenceTaskSpacefromEndEffector
from .SignedDistanceMatrix import SignedDistanceMatrix
from .NearestNeighborIndex import NearestNeighborIndex
from .EndEffectorfromNearestNeighbor import EndEffectorfromNearestNeighbor
from .create_cyclic_data import create_cyclic_data
from .save_matrix_as_heatmap import save_matrix_as_heatmap
from .EndEffectorVisualizationBuilder import EndEffectorVisualizationBuilder
from torch_numpy_converter import to_tensor_double, to_numpy, to_tensor, NTD, to_tensor_without_cuda

'''
[方策のobservationとしてtask_space_positionを使う場合の問題]
- エンドエフェクタの３次元空間中において行動空間を１次元空間のようにして拘束する場合
　定義した task_space 上で0と1のような境界部分で非連続性があるためモデル/方策学習に望ましくない
- ロボットの状態が task_space 上に必ずしも位置しているとは限らないためobservationに対して近似が必要になる
　（バルブと接触状態にある場合には task_space 上から指が外れてしまうことは頻発する）

[行動決定のための擬似的なobservationとしてtask_space_positionを使用する理由]
- task_space_positionを絶対値の空間で自由に決定してしまうと1次元の拘束が意味を持たなくなる
- 例えば[0, 1]の範囲のtask_spaceなのに0.1から次に急に0.4とかの離れた行動をとってしまうと
　明らかに1次元拘束の軌道上から外れてショートカットしたような軌道になってしまう
- これを避けるためには差分入力の形で1stepに動けるtask_space上の距離を制限して行動を実行する必要がある
- 差分行動を決定するためには現在のtask_space_positionが必要となる
- しかし，エンドエフェクタ位置から対応するtask_space_positionを得る逆写像は容易ではない
　（エンドエフェクタ位置が厳密にtask_spaceの軌道上に乗っかっている保証はないため）
- そこであらかじめtask_space上でobservationとなる点の候補を多めに生成しておき，それらとのノルムを測り
　最近棒のものを擬似的な観測として差分制御入力を決定するために用いる
'''

'''
・to_tensor使って GPUに載せるとmultiprocessgin回すときにGPUメモリが無限に増えて止まるので使えない
'''



class Manifold1D_Transformer_Torch(AbstractTaskSpaceTransformer):
    def __init__(self):
        self.num_claw                        = 3
        self.min                             = 0.0
        self.max                             = 1.0
        self.forward_kinematics              = ForwardKinematics()
        self.reference_joint_position        = ReferencePosition().augument_reference_joint_position()
        self.reference_end_effector_position = self.forward_kinematics.calc_1claw(to_tensor_without_cuda(self.reference_joint_position))
        self.reference_end_effector_position = create_cyclic_data(self.reference_end_effector_position) # 中間点を補完する際にはtask_spaceとして閉じている必要がある
        # -----
        reference_task_space                 = ReferenceTaskSpacefromEndEffector()
        self.reference_task_space_position   = reference_task_space.create(self.reference_end_effector_position)
        self.max_euclidean_distance          = reference_task_space.get_max_euclidean_distance()
        # -----
        self.debug = False


    # @abstractmethod
    def task2end(self, task_space_position: TaskSpaceValueObject):
        end_effector_position = [self._task2end_1claw(x) for x in torch.split(task_space_position.value, 1, dim=-1)]
        return EndEffectorPosition(NTD(torch.cat(end_effector_position, dim=-1)))


    def _task2end_1claw(self, task_space_position):
        '''
        - 中間点を補完する際に単純にreference_task_space_positionとのユークリッド距離だけで補完に使用する2点を決定してしまうと
        必ず補完の空洞になる領域が発生してしまい，連続的な行動空間を生成できない（点同士が距離が離れている領域付近で欠落する）
        - なのでtorch.argsort(dist_matrix)から上位2つの近傍点を取得するだけでは正しく補完できない
        - 理由 : reference_task_space_positionにある各点同士の距離は一定ではないため
        - なので, 符号の変化位置を捉えるsigned_distance_matrixを用いる
        '''
        assert len(task_space_position.shape) == 3
        num_data, step, dim         = task_space_position.shape; assert dim==1
        signed_distance_matrix      = SignedDistanceMatrix(is_plot=False).create(task_space_position.reshape(num_data*step,), self.reference_task_space_position)
        index_nearest_neighbor      = NearestNeighborIndex(is_plot=False).get(signed_distance_matrix)
        end_effector_position       = EndEffectorfromNearestNeighbor(
            self.reference_end_effector_position, self.reference_task_space_position, index_nearest_neighbor, self.max_euclidean_distance,
        ).get(task_space_position.reshape(num_data*step,))
        # import ipdb; ipdb.set_trace()
        return end_effector_position.reshape(num_data, step, 3)


    # @abstractmethod
    def end2task(self, end_effector_position):
        _EndEffectorPosition = EndEffectorPosition(NTD(end_effector_position))
        task_space_position  = [self._end2task_1claw(x) for x in torch.split(_EndEffectorPosition.value, self.num_claw, dim=-1)]
        return TaskSpaceValueObject(NTD(torch.cat(task_space_position, dim=-1)))


    def _end2task_1claw(self, end_effector_position):
        num_data, step, dim                      = end_effector_position.shape
        reshaped_end_effector_position           = end_effector_position.reshape(num_data*step, dim).unsqueeze(-1)  # [:, :, torch.newaxis]
        reshaped_reference_end_effector_position = self.reference_end_effector_position.transpose(1, 0).unsqueeze(0)  # [torch.newaxis, :, :]
        distance = torch.linalg.norm(reshaped_end_effector_position - reshaped_reference_end_effector_position, axis=1)
        if self.debug: EndEffectorVisualizationBuilder().build(to_numpy(end_effector_position), to_numpy(self.reference_end_effector_position))
        index_minimum_distance = torch.argsort(distance, axis=1)[:, 0]
        nearest_reference      = torch.take(self.reference_task_space_position, index_minimum_distance)
        return nearest_reference.reshape(num_data, step, -1)



if __name__ == '__main__':

    from robel_dclaw_env.custom_service import visualization as vis
    taskspace = Manifold1D()

    t = torch.linspace(start=0.0, stop=2.0, num=200)
    t = t.reshape(-1, 1)
    t = torch.tile(t, (1, 3))

    end = taskspace.calc(t)

    # vis.scatter_3d(end[:, :3])
    vis.scatter_3d_animation(end[:, :3], num_history=100, interval=10)
