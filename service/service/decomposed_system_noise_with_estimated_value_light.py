import torch



def decomposed_system_noise_with_estimated_value_light(A_t, Sigma_t_diag):
    # 行列積を使わない C_t_diag の計算
    # C_t_diag_simplified = torch.sum((A_t**2) * Sigma_t_diag, dim=1) # for 2D
    C_t_diag_simplified = torch.einsum('bij,bj->bi', A_t**2, Sigma_t_diag)  # (batch_size, n)
    return C_t_diag_simplified
