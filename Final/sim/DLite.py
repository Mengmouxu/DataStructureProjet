import os
import sys
import csv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import Routes_Graph
from data.TrackingInfo import Init_packageLog, Load_packageLog
from utils.Name_config import Name_Ind, Ind_Name
from utils.Center_init import InitCenterStation
from utils.Log_renew import Add_Log_Processing, Add_Log_Sent
from utils.Load_csv import read_csv
import math

def Add_Log_Arrived(package, time, location):
    station_log = {
            "Package ID":package.ID,
            "Time": time,
            "Waiting Time": package.Waitingtime
        }
    if package.read_Log() != None :
        _, last_pos, __ = package.read_Log()
        Stations[last_pos].arrive_history.append(station_log)
    else:
        Stations[location].arrive_history.append(station_log)
    package.add_Log(time, location, 0)
    package.current_location = location
    package.Waitlist.append([package.current_location, time, package.Waitingtime])
    package.Waitingtime = 0
    renew_path(package)

def pred_wait(TimeTable, location, time):
    time_start = int(math.floor(time))
    time_end = int(math.ceil(time))
    wait_time = (float(TimeTable[location][time_start]) + float(TimeTable[location][int(math.ceil(time_end))])) / 2
    return wait_time

def find_next_station(TimeGraph, CostGraph, path, package, time_tick = 1): # 输入该站的paths
    if package.read_Log() != None :
        last_time, last_pos, last_event = package.read_Log()
    else:
        last_time = package.TimeC
        last_pos = package.Src
    if last_pos in path:
        ind_current = path.index(last_pos)
        if package.Category == 0: # 普快
            next_station = path[ind_current + 1]
        if package.Category == 1: # 特快
            next_station = path[ind_current + 1]
            if len(Stations[next_station].storage) > 4 * Stations[next_station].Throughput:
                for i in range(len(TimeGraph)):
                    Stations[i].cost_flag = "star"
                next_station = next_step_new(TimeGraph, TimeTable, package, time_tick = 1)
                for i in range(len(TimeGraph)):
                    Stations[i].cost_flag = "old"
    else:
        next_station = next_step_new(TimeGraph, TimeTable, package, time_tick = 1)
    return next_station

# path 是完全根据log更新的
def renew_path(package):
    if package.read_Log() != None :
        last_time, last_pos, last_event = package.read_Log()
        if last_pos != package.path[-1]:
            package.path.append(last_pos)

def next_step_new(TimeGraph, TimeTable, package, time_tick = 1):
    # 前一篇要么是process要么是初始化arrive
    # 深入预测一/两步
    # 每一层要判断是否达到终点
    # time_tick是站的处理时间
    if package.read_Log() != None :
        _, last_pos, _ = package.read_Log()
    else:
        last_pos = package.Src
    dstar = Dstar()
    path = dstar.run(Stations[last_pos], Stations[package.Dst])
    for m in range(len(Stations)):
            Stations[m].reset()
    return path[1]


def dijkstra_t_advanced(TimeGraph, TimeTable, package):
    src, dst = package.Src, package.Dst
    time = [package.TimeC] * len(TimeGraph)
    distances = [float('inf')] * len(TimeGraph)
    visited = [False] * len(TimeGraph)
    distances[src] = 0
    prev = [-1] * len(TimeGraph)  # Add this line to initialize prev

    for _ in range(len(TimeGraph)):
        min_dist = float('inf')
        min_dist_vertex = -1 # 最短路径顶点索引
        for v in range(len(TimeGraph)):
            if not visited[v] and distances[v] < min_dist:
                min_dist = distances[v]
                min_dist_vertex = v
        visited[min_dist_vertex] = True
        for v in range(len(TimeGraph)): # 更新当前顶点到各点距离
            if not visited[v] and TimeGraph[min_dist_vertex][v] > 0:
                time_now = time[min_dist_vertex]
                if time_now > 150:
                    break 
                wait_time_pred = pred_wait(TimeTable, v, time_now)
                new_dist = distances[min_dist_vertex] + TimeGraph[min_dist_vertex][v] + wait_time_pred * 0.2
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    prev[v] = min_dist_vertex  # Update prev, 记录前驱节点
                    time[min_dist_vertex] = time_now + TimeGraph[min_dist_vertex][v] + Stations[min_dist_vertex].Delay + wait_time_pred

    path = []
    current_vertex = dst
    while current_vertex != -1:
        path.append(current_vertex)
        current_vertex = prev[current_vertex]
    path.reverse()
    return path

def dijkstra_c_advanced(CostGraph, TimeGraph, TimeTable, package): # 只考虑moneycost寻找最优路径
    src, dst = package.Src, package.Dst
    time = [package.TimeC] * len(TimeGraph)
    distances = [float('inf')] * len(CostGraph)
    visited = [False] * len(CostGraph)
    distances[src] = 0
    prev = [-1] * len(CostGraph)  # Add this line to initialize prev

    for _ in range(len(CostGraph)):
        min_dist = float('inf')
        min_dist_vertex = -1 # 最短路径顶点索引
        for v in range(len(CostGraph)):
            if not visited[v] and distances[v] < min_dist:
                min_dist = distances[v]
                min_dist_vertex = v
        visited[min_dist_vertex] = True
        for v in range(len(CostGraph)): # 更新当前顶点到各点距离
            if not visited[v] and CostGraph[min_dist_vertex][v] > 0:
                time_now = time[min_dist_vertex]
                if time_now > 150:
                    break
                wait_time_pred = pred_wait(TimeTable, v, time_now)
                new_dist = distances[min_dist_vertex] + CostGraph[min_dist_vertex][v] + wait_time_pred
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    prev[v] = min_dist_vertex  # Update prev
                    time[min_dist_vertex] = time_now + TimeGraph[min_dist_vertex][v] + Stations[min_dist_vertex].Delay + wait_time_pred * 0.7

    path = []
    current_vertex = dst
    while current_vertex != -1:
        path.append(current_vertex)
        current_vertex = prev[current_vertex]
    path.reverse()
    return path

# event-driven
# 所有待处理的包裹
# 按状态更新时间入队
class PriorityQueue:
    def __init__(self):
        self.queue = []
    # 根据timecreated入队
    def push(self, package, priority):
        if len(self.queue) == 0:
            self.queue.append([package,priority])
            return
        else:
            for i in range(len(self.queue)):
                if priority < self.queue[i][1]:
                    self.queue.insert(i, [package, priority])
                    return
                elif i == len(self.queue) - 1:
                    self.queue.append([package, priority])
                    return
    def pop(self):
        if len(self.queue) == 0:
            return None
        else:
            return self.queue.pop(0)

def simulation(PQ, Stations, Paths, Time_Graph, Cost_Graph, Arrived, time_tick = 1):
    package, last_time = PQ.pop()
    _, last_pos, last_event = package.read_Log()
    if last_pos == package.Dst:
        Arrived.append(package)
        return
    if last_event == 1: # processing
        Add_Log_Sent(package, last_time+Stations[last_pos].Delay, last_pos)
        package.Money_cost += Stations[last_pos].Cost
        PQ.push(package, last_time+Stations[last_pos].Delay)
        return
    elif last_event == 2: # sent
        next_station = find_next_station(TimeGraph, CostGraph, Paths[package.ind], package, time_tick = 1)
        arrive_time = last_time+Time_Graph[last_pos][next_station]
        Add_Log_Arrived(package, arrive_time, next_station)
        package.Money_cost += Cost_Graph[last_pos][next_station]
        if package.Dst == next_station:
            package.Arrived_time = arrive_time
            package.Arrive = True
            Arrived.append(package)
            return
        else:
            Stations[next_station].storage.append(package)
            Stations[next_station].prior_sort()
            PQ.push(package, arrive_time)
            return
    else: # arrived or waiting
        # 根据可处理的余量判断的可以处理的包裹
        buffer = Stations[last_pos].get_buffer(last_time, time_tick)
        if buffer:
            for i in range(len(buffer)):
                if buffer[i].ind == package.ind:
                    Stations[last_pos].storage.pop(i)
                    Stations[last_pos].prior_sort()
                    # 还可以处理的数量减少一个
                    Stations[last_pos].Throughput_left -= 1
                    Add_Log_Processing(package, last_time, last_pos)
                    PQ.push(package, last_time)
                    return
        package.Waitingtime += time_tick
        PQ.push(package, last_time+time_tick)
        return

class Dstar():
    def __init__(self):
        self.open_list = set()
    def min_state(self):
        if not self.open_list:
            return None
        min_state = min(self.open_list, key = lambda x: x.k)
        return min_state
    def get_kmin(self):
        if not self.open_list:
            return -1
        k_min = min([x.k for x in self.open_list])
        return k_min
    def insert(self, state, h_new):
        if state.t == "new":
            state.k = h_new
        elif state.t == "open":
            state.k = min(state.k, h_new)
        elif state.t == "close":
            state.k = min(state.h, h_new)
        state.h = h_new
        state.t = "open"
        self.open_list.add(state)
    def remove(self, state):
        if state.t == "open":
            state.t = "close"
        self.open_list.remove(state)
    def modify_cost(self, state):
        if state.t == "close":
            self.insert(state, state.parent.h + state.cost(state.parent, TimeGraph, TimeTable, time_tick = 1))
    def process_state(self): # !! TimeGraph
        x = self.min_state() # get the state with the min k
        if x is None:
            return -1
        k_old = self.get_kmin() # get the min k
        self.remove(x)
        if k_old < x.h:
            for y_ind in x.get_neighbors():
                y = Stations[y_ind]
                if y.h <= k_old and x.h > y.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1) and y.parent != x:
                    x.parent = y
                    x.h = y.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1)
        if k_old == x.h: 
            for y_ind in x.get_neighbors():
                y = Stations[y_ind]
                if y.t == "new" or (y.parent == x and y.h != x.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1))\
                        or (y.parent != x and y.h > x.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1)):
                    y.parent = x
                    self.insert(y, x.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1))
        else:
            for y_ind in x.get_neighbors():
                y = Stations[y_ind]
                if y.t == "new" or y.parent == x and y.h != x.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1):
                    y.parent = x
                    self.insert(y, x.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1))
                else:
                    if y.parent != x and y.h > x.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1):
                        self.insert(x, x.h)
                    else:
                        if y.parent != x and x.h > y.h + x.cost(y, TimeGraph, TimeTable, time_tick = 1)\
                                and y.t == "close" and y.h > k_old:
                            self.insert(y, y.h)
        return self.get_kmin()
    def modify(self, state):
        self.modify_cost(state)
        while True:
            k_min = self.process_state()
            if k_min >= state.h:
                break
    def run(self, start, end):
        self.insert(end, 0)
        while True:
            self.process_state()
            if start.t == "close":
                break
        s = start
        path = [s.ind]
        while s != end:
            s = s.parent
            path.append(s.ind)
        return path

if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Packages = Init_packageLog(Name_Ind)
    Stations = InitCenterStation(Name_Ind)
    CostGraph, TimeGraph = Routes_Graph()
    TimeTable = read_csv('4000100')
    Paths = []
    for i in range(len(Packages)):
        package = Packages[i]
        if package.Category == 0: # 普快，只考虑cost
            Paths.append(dijkstra_c_advanced(CostGraph, TimeGraph, TimeTable, package))
        if package.Category == 1: # 特快，只考虑time
            Paths.append(dijkstra_t_advanced(TimeGraph, TimeTable, package))
    PQ = PriorityQueue()
    for package in Packages:
        Add_Log_Arrived(package, package.TimeC, package.Src)
        package.current_location = package.Src
        PQ.push(package, package.TimeC)
        Stations[package.Src].storage.append(package)
    for i in range(len(Stations)):
        Stations[i].prior_sort()

    Arrived = []
    stop_package = 10000 
    while len(Arrived) < min(stop_package, len(Packages)) :
        simulation(PQ, Stations, Paths, TimeGraph, CostGraph, Arrived)

    Load_packageLog(PQ.queue+Arrived, Ind_Name)
    
    n_wt = 0
    wait_total_time = 0
    for i in range(min(stop_package, len(Packages))):
        wait_time = 0
        for wait_his in Arrived[i].Waitlist:
            wait_time += wait_his[2]
        if wait_time > 0:
            print(f"Package index: {Packages.index(Arrived[i])}, Waitingtime: {wait_time}")
            n_wt += 1
        wait_total_time += wait_time
    print(f"The number of the package with waiting time is {n_wt}")
    print(f"The total waiting time is {wait_total_time}")
    
    for i in range(len(Stations)):
        Stations[i].arrive_history.sort(key=lambda x: x["Time"])

    while input("Do you want to check the package info? (y/n): ") != "n":
        i = int(input("Input the index of the package you want to check: "))
        print("The package information is as follows: ")
        print("Package Log: ", Packages[i].Log)
        print("Package Path:", Paths[i])
        print("Package Path after further D* Lite optimisation:", Packages[i].path)
        Packages[i].info()
        if Packages[i].Arrive:
            real_time, real_cost = Packages[i].TimeC + Packages[i].Waitingtime,0
            real_path = Packages[i].path
            for s in range(len(real_path)-1):
                real_time += Stations[real_path[s]].Delay
                real_time += TimeGraph[real_path[s]][real_path[s+1]]
                real_cost += Stations[real_path[s]].Cost
                real_cost += CostGraph[real_path[s]][real_path[s+1]]
            print(f"Real Arrived Time: {real_time} "+f" The Difference between real and simulation is {Packages[i].Arrived_time - real_time}")
            print(f"Real Money Cost: {real_cost} "+f" The Difference between real and simulation is {real_cost - Packages[i].Money_cost}")