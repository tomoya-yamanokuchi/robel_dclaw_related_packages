import torch


# シリーズ毎にランダムにシャッフルする関数
def shuffle_series(data, data2):
    shuffled_data = data.clone()


    batch_size, steps, _ = data.shape
    for i in range(batch_size):
        # step方向にランダムな順序を生成
        perm = torch.randperm(steps)
        # ランダムな順序に従ってデータを再配置
        shuffled_data[i] = data[i, perm]
    return shuffled_data


if __name__ == '__main__':
    # ダミーデータの生成
    batch_size = 4
    steps      = 10
    dim        = 3
    data       = torch.randn(batch_size, steps, dim)

    # シャッフルの実行
    shuffled_data = shuffle_series(data)

    # 結果の表示
    print("Original Data:")
    print(data)
    print("\nShuffled Data:")
    print(shuffled_data)


