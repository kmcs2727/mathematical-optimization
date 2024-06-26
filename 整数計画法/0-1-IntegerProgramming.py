import gurobipy as gp
from gurobipy import GRB
from collections import deque
import time

class IntegerProgramming(object):
    def __init__(self, name, capacity, items, costs, weights, zeros=set(), ones=set()):
        self.name = name
        self.capacity = capacity
        self.items = items
        self.costs = costs
        self.weights = weights
        self.zeros = zeros
        self.ones = ones
        # 下界
        self.lb = -100
        # 上界
        self.up = -100
        # 下界をとる最適解
        self.xlb = {j: 0 for j in self.items}
        # 上界をとる最適解
        self.xub = {j: 0 for j in self.items}
        # 分数の品物番号
        self.bi = None

    def getBounds(self):
        temp_capacity = self.capacity.copy()
        for j in self.zeros:
            self.xlb[j] = self.xub[j] = 0
        for j in self.ones:
            self.xlb[j] = self.xub[j] = 1
        for i in range(len(temp_capacity)):
            temp_sum = 0
            for j in self.ones:
                temp_sum = temp_sum + self.weights[i][j]
            temp_capacity[i] -= temp_sum
            if self.capacity[i] < temp_sum:
                self.lb = self.ub = -100
                return 0
        ritems = self.items - self.zeros - self.ones
        """ 下界の取得 """
        for i in ritems:
            flag = 1
            for j in range(len(temp_capacity)):
                if temp_capacity[j] < self.weights[j][i]:
                    flag = 0
            if flag == 1:
                for j in range(len(temp_capacity)):
                    temp_capacity[j] = temp_capacity[j] - weights[j][i]
                self.xlb[i] = 1
        temp_lb = 0
        for i in range(1, len(items) + 1):
            temp_lb = temp_lb + self.xlb[i] * self.costs[i]

        """ 上界の取得 """
        model = gp.Model("relaxed_problem")
        x = model.addVars(self.items, lb=0, ub=1, name="x")
        for i in self.ones:
            model.addConstr(x[i] == 1, name=f"x_{i}_is_1")
        for i in self.zeros:
            model.addConstr(x[i] == 0, name=f"x_{i}_is_0")
        for j in range(len(capacity)):
            model.addConstr(gp.quicksum(self.weights[j][i] * x[i] for i in items) <= capacity[j])
        model.setObjective(gp.quicksum(self.costs[i] * x[i] for i in items), GRB.MAXIMIZE)
        model.optimize()
        if model.status == GRB.OPTIMAL:
            self.ub = model.objVal
            for i in items:
                if 0 < x[i].x < 1:
                    self.bi = i
                elif x[i].x == 1:
                    self.xub[i] =  1
        self.lb = temp_lb

    def __str__(self):
        return "Name: " + self.name + "\n"


def IntegerProgrammingSolve(capacity, items, costs, weights):
    queue = deque()
    root = IntegerProgramming("IP", capacity=capacity, items=items, costs=costs, weights=weights, zeros=set(), ones=set())
    root.getBounds()
    best = root
    queue.append(root)
    opt_val = -1
    opt_ans = {}
    while queue != deque([]):
        p = queue.popleft()
        p.getBounds()
        if p.bi is None:
            if p.ub > opt_val:
                opt_val = p.ub
                opt_ans = p.xub
        else:
            if p.ub > max(best.lb,opt_val):
                if p.lb > best.lb:
                    best = p
                if p.ub > p.lb and p.bi:
                    k = p.bi
                    p1 = IntegerProgramming(p.name + '+' + str(k), capacity=p.capacity, items=p.items, costs=p.costs,
                                            weights=p.weights, zeros=p.zeros, ones=p.ones.union({k}))
                    queue.append(p1)
                    p2 = IntegerProgramming(p.name + '-' + str(k), capacity=p.capacity, items=p.items, costs=p.costs,
                                            weights=p.weights, zeros=p.zeros.union({k}), ones=p.ones)
                    queue.append(p2)
    if opt_val > best.lb:
        return "Optimal", opt_val, opt_ans
    else:
        return "Optimal", best.lb, best.xlb

print("テストケース文をそのまま貼り付けてください")
N, M, opt = map(float, input().split())
N = int(N)
M = int(M)
items = {i+1 for i in range(N)}
data = list(map(float, input().split()))
costs = {i+1: data[i] for i in range(N)}
weights = []
for i in range(M):
    data = list(map(int, input().split()))
    temp = {j+1: data[j] for j in range(N)}
    weights.append(temp)
capacity = list(map(int, input().split()))
start = time.time()
res = IntegerProgrammingSolve(capacity=capacity, items=items, costs=costs, weights=weights)
end = time.time()
print("想定される最適解", opt)
print("最適値 = ", res[1])
print("最適解 = ", res[2])
print("実行時間: ", round(end - start, 4))
