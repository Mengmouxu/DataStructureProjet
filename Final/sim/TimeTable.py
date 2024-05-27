"""
得出TimeTable
"""
import yaml
import sys
import os
import csv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import Routes_Graph
from data.TrackingInfo import Init_packageLog_queue
from utils.Name_config import Name_Ind, Ind_Name
from utils.Center_init import InitCenterStation
from utils.Packages_gen import packages_gen
from utils.Load_csv import write_csv
from utils.Log_renew import Add_Log_Processing, Add_Log_Sent

def write_yaml(data, yaml_path):
    with open(''.join(["config/", yaml_path, ".yaml"]), encoding="utf-8", mode="a") as f:
        yaml.dump(data, stream=f, allow_unicode=True)

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
    package.Waitlist.append([package.current_location, time, package.Waitingtime])
    package.current_location = location
    package.Waitingtime = 0


def dijkstra_t(TimeGraph, package): # 只考虑timecost寻找最优路径
    src, dst = package.Src, package.Dst
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
                new_dist = distances[min_dist_vertex] + TimeGraph[min_dist_vertex][v]
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    prev[v] = min_dist_vertex  # Update prev

    path = []
    current_vertex = dst
    while current_vertex != -1:
        path.append(current_vertex)
        current_vertex = prev[current_vertex]
    path.reverse()
    return path

def dijkstra_c(CostGraph, package): # 只考虑moneycost寻找最优路径
    src, dst = package.Src, package.Dst
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
                new_dist = distances[min_dist_vertex] + CostGraph[min_dist_vertex][v]
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    prev[v] = min_dist_vertex  # Update prev

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
    # print(len(PQ.queue))
    package, last_time = PQ.pop()
    _, last_pos, last_event = package.read_Log()
    routes = Paths[package.ind]
    next_station = routes[routes.index(last_pos) + 1]
    if last_pos == package.Dst:
        Arrived.append(package)
        return
    if last_event == 1: # processing
        Add_Log_Sent(package, last_time+Stations[last_pos].Delay, last_pos)
        package.Money_cost += Stations[last_pos].Cost
        PQ.push(package, last_time+Stations[last_pos].Delay)
        return
    elif last_event == 2: # sent
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
                    # print(Stations[last_pos].Throughput_left)
                    return
        package.Waitingtime += time_tick
        PQ.push(package, last_time+time_tick)
        return
    
def simul():
    Paths = []
    Stations_log = []
    for i in range(len(Packages)):
        package = Packages[i]
        if package.Category == 0: # 普快，只考虑cost
            Paths.append(dijkstra_c(CostGraph, package))
        if package.Category == 1: # 特快，只考虑time
            Paths.append(dijkstra_t(TimeGraph, package))
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
    n_wt = 0
    wait_total = 0
    for i in range(min(stop_package, len(Packages))):
        wait_total_time = 0
        for wait_his in Arrived[i].Waitlist:
            wait_total_time += wait_his[2]
        if wait_total_time > 0:
            wait_total += wait_total_time
            n_wt += 1
    for i in range(len(Stations)):
        Stations[i].arrive_history.sort(key=lambda x: x["Time"])
        Stations_log.append(Stations[i].arrive_history)
    return Stations_log


if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    TimeGraph, CostGraph = Routes_Graph()
    TimeTable = [[0.0] * 200] * 30
    for simul_time in range(100):
        Stations = InitCenterStation(Name_Ind)
        packages_gen()
        Packages = Init_packageLog_queue(Name_Ind)
        Stations_log = simul()
        for station_ind in range(len(Stations_log)):
            station_log = Stations_log[station_ind]
            num_log = len(station_log)
            thre_n = 0
            threshold = 0
            thre_time = 0
            for i in range(num_log):
                flag = 0
                log  = station_log[i]
                time = log['Time']
                waiting_time = log['Waiting Time']
                if time - threshold < 1:
                    thre_time += waiting_time
                    thre_n += 1
                    continue
                threshold += 1
                if thre_n == 0:
                        Stations[station_ind].queue_time_table[threshold]
                else:
                    Stations[station_ind].queue_time_table[threshold] = thre_time / thre_n
                thre_n = 0
                thre_time = 0
                while time - threshold > 1:
                    Stations[station_ind].queue_time_table[threshold] = 0.0
                    threshold += 1
                    flag = 1
                if i == num_log - 1 and flag:
                    Stations[station_ind].queue_time_table[threshold] = waiting_time
        for ind in range(30):
            TimeTable[ind] = [a + b for a, b in zip(TimeTable[ind], Stations[ind].queue_time_table)]
    for m in range(len(TimeTable)):
        for n in range(len(TimeTable[m])):
            TimeTable[m][n] /= 100
    write_csv(TimeTable, "4000100")
