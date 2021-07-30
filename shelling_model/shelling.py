import numpy as np
import random


class Schelling:
    def __init__(self, size, empty_ratio, similarity_threshold, n_neighbors, Pauto):
        self.size = size  # 居住可能人数
        self.empty_ratio = empty_ratio  # 空き家の割合
        self.similarity_threshold = similarity_threshold  # 閾値
        self.n_neighbors = n_neighbors  # どこまでの範囲見るか
        self.Pauto = Pauto  # 自動引越しする確率

        # 黒人、白人、空き家 の設置確率リスト
        p = [(1 - empty_ratio) / 2, (1 - empty_ratio) / 2, empty_ratio]
        city_size = int(np.sqrt(self.size)) ** 2
        # (city_size, 1)のベクトル生成 (人種１=-1, 人種2=1, 空き家=0)
        self.city = np.random.choice([-1, 1, 0], size=city_size, p=p)
        # 2D に変換 (座標に)
        self.city = np.reshape(
            self.city, (int(np.sqrt(city_size)), int(np.sqrt(city_size)))
        )
        # 総住民数
        self.num_people = len(np.where(self.city != 0)[0])

        # 住民座標リスト
        x_list, y_list = np.where(self.city != 0)
        self.resident_pos = list(zip(x_list, y_list))
        # 空き地の座標リスト
        x_list, y_list = np.where(self.city == 0)
        self.empty_house_pos = list(zip(x_list, y_list))

    def serch_neighbors(self, row, col):
        """ 近隣の取得 """
        if row - self.n_neighbors < 0 and col - self.n_neighbors < 0:
            neighborhood = self.city[
                0 : row + self.n_neighbors + 1,
                0 : col + self.n_neighbors + 1,
            ]
        elif row - self.n_neighbors < 0:
            neighborhood = self.city[
                0 : row + self.n_neighbors + 1,
                col - self.n_neighbors : col + self.n_neighbors + 1,
            ]
        elif col - self.n_neighbors < 0:
            neighborhood = self.city[
                row - self.n_neighbors : row + self.n_neighbors + 1,
                0 : col + self.n_neighbors + 1,
            ]
        else:
            neighborhood = self.city[
                row - self.n_neighbors : row + self.n_neighbors + 1,
                col - self.n_neighbors : col + self.n_neighbors + 1,
            ]

        return neighborhood

    def neighbor_similality(self, row, col):
        """ 近隣の情報計算 """
        # 選ばれた人種
        race = self.city[row, col]
        # 近隣の取得
        neighborhood = self.serch_neighbors(row, col)
        # 近隣の大きさ
        neighborhood_size = np.size(neighborhood) - 1
        # 0の数 (= 近隣の空き家の数)
        n_empty_houses = len(np.where(neighborhood == 0)[0])
        # 同人種数 (自分も含まれるため -1)
        same_race = len(np.where(neighborhood == race)[0]) - 1
        # 異人種数
        diff_race = len(np.where(neighborhood == -race)[0])

        if same_race + diff_race == 0:
            similality_rate = None
        else:
            # 同人種の割合
            similality_rate = same_race / (same_race + diff_race)

        return similality_rate, diff_race, (neighborhood_size, n_empty_houses)

    def random_move(self, pos_list):
        """ 空き地へランダムに引っ越し(空き地ならどこでも引っ越し可能) """
        # 引っ越し先(空き地)座標リスト
        selected_empty_poss = random.sample(self.empty_house_pos, k=len(pos_list))

        for (now_r, now_c), (move_r, move_c) in zip(pos_list, selected_empty_poss):
            # 引っ越し
            race = self.city[now_r, now_c]
            self.city[move_r, move_c] = race
            self.city[now_r, now_c] = 0

            # 空き地リストの更新
            self.empty_house_pos.remove((move_r, move_c))
            self.empty_house_pos.append((now_r, now_c))

            # 住民座標リストの更新
            self.resident_pos.remove((now_r, now_c))
            self.resident_pos.append((move_r, move_c))

    def move_judge(self, num_move=100):
        """ 複数の住民を選択して状況に応じて引っ越すかどうかを判定 """
        # 特に指定がない場合はランダムに住人を選択
        selected_poss = random.sample(self.resident_pos, k=num_move)

        # 引っ越す人の座標リスト
        move_resident_pos = []
        for row, col in selected_poss:
            # 同人種割合,  異人種数 の計算
            sim_rate, diff_race, _ = self.neighbor_similality(row, col)
            # 違う人種の人が一人もいない
            if diff_race == 0:
                # 自動引っ越し
                if np.random.rand() < self.Pauto:
                    # 引っ越し
                    # self.random_move(row, col)
                    move_resident_pos.append((row, col))

            # 周りの状況次第で引っ越す (同種の割合が閾値を下回る or 自動引っ越し)
            elif sim_rate < self.similarity_threshold or np.random.rand() < self.Pauto:
                # 引っ越し
                # self.random_move(row, col)
                move_resident_pos.append((row, col))

        return move_resident_pos

    def run(self, num_move=100):
        """ 選択と引っ越しの実行 """
        selected_poss = self.move_judge(num_move)
        self.random_move(selected_poss)

    def get_mean_similarity_ratio(self):
        """ 住民の近隣の同人種割合 (平均) """
        count = 0
        similarity_ratio = 0
        for (row, col), value in np.ndenumerate(self.city):
            race = self.city[row, col]
            if race != 0:
                # 同人種割合,  異人種数 の計算
                (
                    sim_rate,
                    diff_race,
                    (neighborhood_size, n_empty_houses),
                ) = self.neighbor_similality(row, col)
                if neighborhood_size != n_empty_houses:
                    similarity_ratio += sim_rate
                    count += 1
        return similarity_ratio / count