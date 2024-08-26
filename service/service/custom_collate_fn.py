import torch


def custom_collate_fn(batch):
    batch_dict = {key: [] for key in batch[0][0].keys()}
    for sample in batch:
        for item in sample:
            for key, value in item.items():
                batch_dict[key].append(value)

    # Convert lists to tensors
    for key in batch_dict:
        if isinstance(batch_dict[key][0], torch.Tensor):
            batch_dict[key] = torch.stack(batch_dict[key])
        elif isinstance(batch_dict[key][0], (int, float)):
            batch_dict[key] = torch.tensor(batch_dict[key])

    return batch_dict
