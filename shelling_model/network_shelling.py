import networkx as nx
import numpy as np
import random


class Network_Schelling:
    def __init__(self, size, parameter, empty_ratio, similarity_threshold, Pauto):
        self.size = size  # 居住可能人数 (number of nodes)
        self.empty_ratio = empty_ratio  # 空き家の割合
        self.similarity_threshold = similarity_threshold  # 閾値
        self.Pauto = Pauto  # 自動引越しする確率

        # 黒人、白人、空き家 の設置確率リスト
        p = [(1 - empty_ratio) / 2, (1 - empty_ratio) / 2, empty_ratio]
        # (city_size, 1)のベクトル生成 (人種１=-1, 人種2=1, 空き家=0)
        self.city = np.random.choice([-1, 1, 0], size=size, p=p)

        # 総住民数
        self.num_people = len(np.where(self.city != 0)[0])

        # 住民がいるノード番号リスト
        self.resident_num = list(np.where(self.city != 0)[0])
        # 空き地のノード番号リスト
        self.num_empty = list(np.where(self.city == 0)[0])

        # networkの作成
        self.G = nx.barabasi_albert_graph(size, parameter)
        # 各ノードに住民 or 空き地のラベルを追加
        for i in range(size):
            self.G.nodes[i]["kind"] = self.city[i]

    def neighbor_similality(self, n):
        """ 近隣情報の取得 """
        race = self.G.nodes[n]["kind"]
        neighbors = list(nx.neighbors(self.G, n))
        info = np.array([self.G.nodes[i]["kind"] for i in neighbors])

        # 空き家の数
        n_empty_houses = np.sum(info == 0)
        # 同人種数 (自分も含まれるため -1)
        same_race = np.sum(info == race)
        # 異人種数
        diff_race = np.sum(info == -race)

        if same_race + diff_race == 0:
            similality_rate = None
        else:
            # 同人種の割合
            similality_rate = same_race / (same_race + diff_race)

        return similality_rate, diff_race, (len(neighbors), n_empty_houses)

    def random_move(self, pos_list):
        """ 空き地へランダムに引っ越し(空き地ならどこでも引っ越し可能) """
        # 引っ越し先(空き地)座標リスト
        selected_empty_poss = random.sample(self.num_empty, k=len(pos_list))

        for now, move in zip(pos_list, selected_empty_poss):
            # 引っ越し
            race = self.G.nodes[now]["kind"]
            self.G.nodes[move]["kind"] = race
            self.G.nodes[now]["kind"] = 0

            # 空き地リストの更新
            self.num_empty.remove(move)
            self.num_empty.append(now)

            # 住民座標リストの更新
            self.resident_num.remove(now)
            self.resident_num.append(move)

    def move_judge(self, num_move=100):
        """ 複数の住民を選択して状況に応じて引っ越すかどうかを判定 """
        # ランダムに住人を選択(複数)
        selected_poss = random.sample(self.resident_num, k=num_move)

        # 引っ越す人の座標リスト
        move_resident_pos = []
        for n in selected_poss:
            # 同人種割合,  異人種数 の計算
            sim_rate, diff_race, _ = self.neighbor_similality(n)
            # 違う人種の人が一人もいない
            if diff_race == 0:
                # 自動引っ越し
                if np.random.rand() < self.Pauto:
                    # 引っ越し
                    # self.random_move(row, col)
                    move_resident_pos.append(n)

            # 周りの状況次第で引っ越す (同種の割合が閾値を下回る or 自動引っ越し)
            elif sim_rate < self.similarity_threshold or np.random.rand() < self.Pauto:
                # 引っ越し
                move_resident_pos.append(n)

        return move_resident_pos

    def run(self, num_move=100):
        """ 選択と引っ越しの実行 """
        selected_poss = self.move_judge(num_move)
        self.random_move(selected_poss)

    def get_mean_similarity_ratio(self):
        """ 住民の近隣の同人種割合 (平均) """
        count = 0
        similarity_ratio = 0
        for n in range(self.size):
            race = self.G.nodes[n]["kind"]
            if race != 0:
                # 同人種割合,  異人種数 の計算
                (
                    sim_rate,
                    diff_race,
                    (neighborhood_size, n_empty_houses),
                ) = self.neighbor_similality(n)
                if neighborhood_size != n_empty_houses:
                    similarity_ratio += sim_rate
                    count += 1
        return similarity_ratio / count
