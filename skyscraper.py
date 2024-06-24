from gurobipy import *

directions = ["U", "D", "L", "R"]


def solve_skyscraper(size, see):
    model = Model("skyscraper")

    # 変数定義1
    """
    g[i,j,k] = 1: i行j列に高さkの建物がある
    g[i,j,k] = 0: i行j列に高さkの建物がない
    """
    g = {}
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                g[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")

    # 変数定義2
    """
    U[i,j,k] = 1: i行j列にある高さkの建物が上から見える
    U[i,j,k] = 0: i行j列にある高さkの建物が上から見えない
    """
    U = {}
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                U[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"U_{i}_{j}_{k}")

    # 変数定義3
    """
    D[i,j,k] = 1: i行j列にある高さkの建物が下から見える
    D[i,j,k] = 0: i行j列にある高さkの建物が下から見えない
    """
    D = {}
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                D[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"D_{i}_{j}_{k}")

    # 変数定義4
    """
    L[i,j,k] = 1: i行j列にある高さkの建物が左から見える
    L[i,j,k] = 0: i行j列にある高さkの建物が左から見えない
    """
    L = {}
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                L[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"L_{i}_{j}_{k}")

    # 変数定義5
    """
    R[i,j,k] = 1: i行j列にある高さkの建物が右から見える
    R[i,j,k] = 0: i行j列にある高さkの建物が右から見えない
    """
    R = {}
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                R[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"R_{i}_{j}_{k}")

    # それぞれのマスには建物は一つだけ置く
    for i in range(size):
        for j in range(size):
            model.addConstr(quicksum(g[i, j, k] for k in range(1, size + 1)) == 1)

    # それぞれ列はユニークな高さの建物が並ぶ
    for i in range(size):
        for k in range(1, size + 1):
            model.addConstr(quicksum(g[i, j, k] for j in range(size)) == 1)

    # それぞれ行はユニークな高さの建物が並ぶ
    for j in range(size):
        for k in range(1, size + 1):
            model.addConstr(quicksum(g[i, j, k] for i in range(size)) == 1)

    # U,D,R,Lの設定
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                # U[i, j, k]の設定
                model.addConstr(U[i, j, k] <= g[i, j, k])
                for I in range(i):
                    for K in range(k + 1, size + 1):
                        model.addConstr(U[i, j, k] + g[I, j, K] <= 1)
                if i == 0 or k == size:
                    model.addConstr(U[i, j, k] == g[i, j, k])
                else:
                    model.addConstr(
                        U[i, j, k] >= g[i, j, k] - i + quicksum(g[I, j, K] for I in range(i) for K in range(1, k))
                    )

                # D[i, j, k]の設定
                model.addConstr(D[i, j, k] <= g[i, j, k])
                for I in range(i + 1, size):
                    for K in range(k + 1, size + 1):
                        model.addConstr(D[i, j, k] + g[I, j, K] <= 1)
                if i == size - 1 or k == size:
                    model.addConstr(D[i, j, k] == g[i, j, k])
                else:
                    model.addConstr(
                        D[i, j, k] >= g[i, j, k] - (size - i - 1) + quicksum(
                            g[I, j, K] for I in range(i + 1, size) for K in range(1, k))
                    )

                # L[i, j, k]の設定
                model.addConstr(L[i, j, k] <= g[i, j, k])
                for J in range(j):
                    for K in range(k + 1, size + 1):
                        model.addConstr(L[i, j, k] + g[i, J, K] <= 1)
                if j == 0 or k == size:
                    model.addConstr(L[i, j, k] == g[i, j, k])
                else:
                    model.addConstr(
                        L[i, j, k] >= g[i, j, k] - j + quicksum(g[i, J, K] for J in range(j) for K in range(1, k))
                    )

                # R[i, j, k]の設定
                model.addConstr(R[i, j, k] <= g[i, j, k])
                for J in range(j + 1, size):
                    for K in range(k + 1, size + 1):
                        model.addConstr(R[i, j, k] + g[i, J, K] <= 1)
                if j == size - 1 or k == size:
                    model.addConstr(R[i, j, k] == g[i, j, k])
                else:
                    model.addConstr(
                        R[i, j, k] >= g[i, j, k] - (size - j - 1) + quicksum(
                            g[i, J, K] for J in range(j + 1, size) for K in range(1, k))
                    )

    for (direction, j), v in see.items():
        if direction == "U":
            model.addConstr(v == quicksum(U[i, j, k] for i in range(size) for k in range(1, size + 1)))
        if direction == "D":
            model.addConstr(v == quicksum(D[i, j, k] for i in range(size) for k in range(1, size + 1)))
        if direction == "L":
            model.addConstr(v == quicksum(L[j, i, k] for i in range(size) for k in range(1, size + 1)))
        if direction == "R":
            model.addConstr(v == quicksum(R[j, i, k] for i in range(size) for k in range(1, size + 1)))

    # 目的関数(なし)
    model.setObjective(0, GRB.MINIMIZE)

    # 最適化実行
    model.optimize()

    # 出力確認
    if model.status == GRB.OPTIMAL:
        print("Solution found!")
        gg = []
        for i in range(size):
            col = []
            for j in range(size):
                for k in range(1, size + 1):
                    if g[i, j, k].X > 0.5:  # セル(i, j) に建物 k が配置されている場合
                        col.append(k)
            gg.append(col)

        for i in range(size):
            print(gg[i])
    else:
        print("No solution found")

"""
出力テスト1
"""

# グリッドのサイズ
size1 = 5

# 見え方の制約
see1 = {
    ("U", 0): 5,
    ("R", 4): 5,
}

# 実行
solve_skyscraper(size1, see1)