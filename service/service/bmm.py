import torch


def bmm(src: str, dest: str, new_name: str) -> None:
    return torch.bmm(A, ft.unsqueeze(-1)).squeeze(-1)


if __name__ == '__main__':
    # 使用例
    src      = '/nfs/monorepo_ral2023/robel_dclaw_env/robel_dclaw_env/domain/environment/model/pushing_object/object_current.xml'
    dest     = '/nfs/monorepo_ral2023/env_dataset'

    new_name = 'koko.xml'
    file_copy_and_rename(src, dest, new_name)
