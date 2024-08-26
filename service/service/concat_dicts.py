import torch
from collections import defaultdict
# from torch_numpy_converter import to_numpy



def concat_dicts(dict_list):
    concat_dict = defaultdict(list)
    for d in dict_list:
        for key, value in d.items():
            # valueがPyTorchのテンソルでスカラー値である場合にitem()で数値に変換
            if isinstance(value, torch.Tensor):
                value = value.item()
            concat_dict[key].append(value)
    return dict(concat_dict)
