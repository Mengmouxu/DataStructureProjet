"""
用TimeTable实时更新每一步，但会陷入死循环
"""
import sys
import os
import math
import csv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import Routes_Graph
from data.TrackingInfo import Init_packageLog, Load_packageLog
from utils.Name_config import Name_Ind, Ind_Name
from utils.Center_init import InitCenterStation
from utils.Log_renew import Add_Log_Processing, Add_Log_Sent


def read_csv(csv_path):
    data = []
    with open(''.join(["config/", csv_path, ".csv"]), encoding="utf-8", mode="r") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if row:
                data.append(row)
    return data

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
    renew_path(package)
    package.Waitlist.append([package.current_location, time, package.Waitingtime])
    package.current_location = location
    package.Waitingtime = 0

def find_next_station(TimeGraph, CostGraph, package, time_tick = 1):
    if package.read_Log() != None :
        last_time, last_pos, last_event = package.read_Log()
        time_start = last_time + time_tick
    else:
        last_time = package.TimeC
        last_pos = package.Src
        last_event = 0
        time_start = last_time + package.Waitingtime
    if package.Category == 0: # 普快
        path = dijkstra_c(CostGraph, package)
        ind_current = path.index(last_pos)
        next_station = path[ind_current + 1]
    if package.Category == 1: # 特快
        next_station = next_step(TimeGraph, package, time_tick = 1)
    return next_station

# path 是完全根据log更新的
def renew_path(package):
    if package.read_Log() != None :
        last_time, last_pos, last_event = package.read_Log()
        if last_pos != package.path[-1]:
            package.path.append(last_pos)

def next_step(TimeGraph, package, time_tick = 1):
    # 前一篇要么是process要么是初始化arrive
    # 深入预测一/两步
    # 每一层要判断是否达到终点
    # time_tick是站的处理时间
    dst = package.Dst
    if package.read_Log() != None :
        last_time, last_pos, last_event = package.read_Log()
        time_start = last_time + time_tick
    else:
        last_time = package.TimeC
        last_pos = package.Src
        last_event = 0
        time_start = last_time + package.Waitingtime
    arr_next_time = [time_start] * len(TimeGraph)
    expected_waiting_time = [0.0] * len(TimeGraph)
    expected_timecost = [0.0] * len(TimeGraph)
    for v in range(len(TimeGraph)):
        # TimeTable = read_csv('400010')
        arr_next_time[v] = arr_next_time[v] + Stations[last_pos].Delay + TimeGraph[last_pos][v]
        time_s = int(math.floor(arr_next_time[v]))
        time_e = int(math.ceil(arr_next_time[v]))
        #print(v)
        #print(time_s)
        #print(time_e)
        if time_e <= 199:
            expected_waiting_time[v] = (float(TimeTable[v][time_s]) + float(TimeTable[v][time_e])) / 2
        else:
            expected_waiting_time[v] = 0
        expected_timecost[v] = arr_next_time[v] + expected_waiting_time[v]
    expected_timecost[last_pos] = 1000000
    min_timecost = min(expected_timecost)
    next_station = expected_timecost.index(min_timecost)
    return next_station


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
    # next_station = routes[routes.index(last_pos) + 1]
    if last_pos == package.Dst:
        Arrived.append(package)
        return
    if last_event == 1: # processing
        Add_Log_Sent(package, last_time+Stations[last_pos].Delay, last_pos)
        package.Money_cost += Stations[last_pos].Cost
        PQ.push(package, last_time+Stations[last_pos].Delay)
        return
    elif last_event == 2: # sent
        next_station = find_next_station(TimeGraph, CostGraph, package, time_tick = 1)
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


"""
if __name__ == "__main__":
    packages_gen()
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Stations = InitCenterStation(Name_Ind)
    Packages = Init_packageLog_queue(Name_Ind)
    TimeGraph, CostGraph = Routes_Graph()
    Stations_log = simul()
    # print(Stations_log[17])
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
            # print(threshold)
            if thre_n == 0:
                    # Stations[station_ind].queue_time_table.append(0.0)
                    Stations[station_ind].queue_time_table[threshold]
            else:
                # Stations[station_ind].queue_time_table.append(thre_time / thre_n)
                Stations[station_ind].queue_time_table[threshold] = thre_time / thre_n
            thre_n = 0
            thre_time = 0
            while time - threshold > 1:
                # Stations[station_ind].queue_time_table.append(0.0)
                Stations[station_ind].queue_time_table[threshold] = 0.0
                threshold += 1
                flag = 1
            if i == num_log - 1 and flag:
                Stations[station_ind].queue_time_table[threshold] = waiting_time
    # print(Stations_log[-1][-1])
    # print(Stations[-1].queue_time_table[:50])
"""

if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Stations = InitCenterStation(Name_Ind)
    Packages = Init_packageLog(Name_Ind)
    TimeGraph, CostGraph = Routes_Graph()
    TimeTable = read_csv('4000100')
    Paths = []
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
    print(f"The number of the package is {len(PQ.queue)}")
    Arrived = []
    # stop_package = input("> Input the number of the package you want to stimulate: ")
    stop_package = 10000 
    while len(Arrived) < min(stop_package, len(Packages)) :
        simulation(PQ, Stations, Paths, TimeGraph, CostGraph, Arrived)

    Load_packageLog(PQ.queue+Arrived, Ind_Name)

    n_wt = 0
    for i in range(min(stop_package, len(Packages))):
        # if Arrived[i].Waitingtime > 0:
        wait_total_time = 0
        for wait_his in Arrived[i].Waitlist:
            wait_total_time += wait_his[2]
        if wait_total_time > 0:
            print(f"Package index: {Packages.index(Arrived[i])}, Waitingtime: {wait_total_time}")
            n_wt += 1
    print(f"The number of the package with waiting time is {n_wt}")
    for i in range(len(Stations)):
        Stations[i].arrive_history.sort(key=lambda x: x["Time"])
    for i in range(10):
        print(i)
        print(Paths[i])
        print(Packages[i].path)

    while input("Do you want to check the package info? (y/n): ") != "n":
        i = int(input("Input the index of the package you want to check: "))
        print("The package information is as follows: ")
        print("Package Log: ", Packages[i].Log)
        print("Package Path:", Paths[i])
        print("Package new Path:", package[i].path)
        Packages[i].info()
        if Packages[i].Arrive:
            real_time, real_cost = Packages[i].TimeC + Packages[i].Waitingtime,0
            for s in range(len(Paths[i])-1):
                real_time += Stations[Paths[i][s]].Delay
                real_time += TimeGraph[Paths[i][s]][Paths[i][s+1]]
                real_cost += Stations[Paths[i][s]].Cost
                real_cost += CostGraph[Paths[i][s]][Paths[i][s+1]]
            print(f"Real Arrived Time: {real_time} "+f" The Difference between real and simulation is {real_time - Packages[i].Arrived_time}")
            print(f"Real Money Cost: {real_cost} "+f" The Difference between real and simulation is {real_cost - Packages[i].Money_cost}")
