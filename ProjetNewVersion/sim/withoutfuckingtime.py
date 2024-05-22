import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import Routes_Graph
from data.TrackingInfo import Init_packageLog
from utils.Name_config import Name_Ind, Ind_Name
from sim.InitCenter import InitCenterStation
import time

def Add_Log_Arrived(package, time, location):
    package.add_Log(time, location, 0)

def Add_Log_Processing(package, time, location):
    package.add_Log(time, location, 1)

def Add_Log_Sent(package, time, location):
    package.add_Log(time, location, 2)

def Add_Log_Waiting(package, time, location):
    package.add_Log(time, location, 3)

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


class PriorityQueue:
    def __init__(self):
        self.queue = []
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
            PQ.push(package, arrive_time)
            return
    else: # arrived or waiting
        buffer = Stations[last_pos].get_buffer(last_time, time_tick)
        if buffer != []:
            for i in range(len(buffer)):
                if buffer[i].ind == package.ind:
                    Stations[last_pos].storage.pop(i)
                    # Stations[last_pos].Throughput_left -= 1
                    Add_Log_Processing(package, last_time, last_pos)
                    PQ.push(package, last_time)
                    return
        package.Waitingtime += time_tick
        PQ.push(package, last_time+time_tick)
        return
        
                

if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Stations = InitCenterStation(Name_Ind)
    Packages = Init_packageLog(Name_Ind)
    TimeGraph, CostGraph = Routes_Graph()
    # Paths = [dijkstra_t(TimeGraph, package=Packages[i]) for i in range(len(Packages))]
    # 找到所有包裹的路径
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
        PQ.push(package, package.TimeC)
        Stations[package.Src].storage.append(package)
    print(f"The number of the package is {len(PQ.queue)}")
    Arrived = []
    # stop_package = input("> Input the number of the package you want to stimulate: ")
    stop_package = 10000 
    while len(Arrived) < min(stop_package, len(Packages)) :
        simulation(PQ, Stations, Paths, TimeGraph, CostGraph, Arrived)
    for i in range(min(stop_package, len(Packages))):
        if Arrived[i].Waitingtime > 0:
            print(Arrived[i].Waitingtime)
            print(Packages.index(Arrived[i]))
    while input("Do you want to check the package info? (y/n): ") != "n":
        i = int(input("Input the index of the package you want to check: "))
        print("The package information is as follows: ")
        print("Package Log: ", Packages[i].Log)
        print("Package Path:", Paths[i])
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


