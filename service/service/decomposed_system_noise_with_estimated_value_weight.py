import torch



def decomposed_system_noise_with_estimated_value_weight(A_t, Sigma_t_diag):
    # 行列積を使う C_t_diag の計算
    Sigma_t  = torch.diag(Sigma_t_diag)
    C_t      = A_t @ Sigma_t @ A_t.t()
    C_t_diag = torch.diag(C_t)
    return C_t_diag
