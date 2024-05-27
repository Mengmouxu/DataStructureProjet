import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import Routes_Graph
from data.TrackingInfo import Init_packageLog
from utils.Name_config import Name_Ind, Ind_Name
from utils.Center_init import InitCenterStation
from utils.Log_renew import Add_Log_Processing, Add_Log_Sent
import time

def Add_Log_Arrived(package, time, location):
    package.add_Log(time, location, 0)

def Package_Process(package, stations, routes,\
                    time_begin, Time_Graph, Cost_Graph,\
                    time_tick = 1):
    """
    Here, the i represents the index of the package in the Packages
    routes represents the stations of the package will pass
    stations represents the information of all the centers and stations
    """
    time_now = time.time()
    t = (time_now - time_begin) * time_tick
    if package.read_Log() == None and t >= package.TimeC:
        Add_Log_Arrived(package, package.TimeC, package.Src)
        stations[package.Src].package_queue.enqueue(package)
        return
    if package.read_Log() != None:
        last_time, last_pos, last_event = package.read_Log()
        past_time = t - last_time # 距离上一次状态更新的时间
        next_station = routes[routes.index(last_pos) + 1]
        """
        event = 0 -> ARRIVED \\
        event = 1 -> PROCESSING \\
        event = 2 -> SENT \\
        events = ["ARRIVED", "PROCESSING", "SENT"]
        """
        if last_event == 1: # processing
            if past_time >= stations[last_pos].Delay: # 处理时间超过该站的delay，sent
                Add_Log_Sent(package, last_time + stations[last_pos].Delay, last_pos)
                package.Money_cost += stations[last_pos].Cost
                stations[last_pos].remove_prepared(package) # 将包裹从站的prepared queue移除
                if past_time >= stations[last_pos].Delay + Time_Graph[last_pos][next_station]:
                    arrived_time = last_time + stations[last_pos].Delay + Time_Graph[last_pos][next_station]
                    Add_Log_Arrived(package, arrived_time, next_station) #更新状态arrived
                    if package.Dst == next_station: #到达目的地
                        package.Arrive = True
                        package.Arrived_time = arrived_time
                        package.Money_cost += Cost_Graph[last_pos][next_station]
                    else: #未到达目的地，中转
                        stations[next_station].package_queue.enqueue(package)
                        package.Money_cost += Cost_Graph[last_pos][next_station]
        elif last_event == 2: #sent，判断是否到达
            if past_time >= Time_Graph[last_pos][next_station]:
                arrived_time = last_time + Time_Graph[last_pos][next_station]
                Add_Log_Arrived(package, arrived_time, next_station)
                if package.Dst == next_station: #到达目的地
                    package.Arrive = True
                    package.Arrived_time = arrived_time
                    package.Money_cost += Cost_Graph[last_pos][next_station]
                else: #中转
                    stations[next_station].package_queue.enqueue(package)
                    # package.Money_cost += stations[last_pos].Cost
                    package.Money_cost += Cost_Graph[last_pos][next_station]


"""
# 在buffer库中的是正在处理的
def Queue_Buffer(station, time_begin, time_tick = 1): # 更新buffer_pool
    time_now = time.time()
    t = (time_now - time_begin) * time_tick
    buffer_pool = station.buffer
    # 先看buffer_pool是否可移出包裹
    # 即库中包裹是否已过time_tick
    # 若已过一个timetick，移出buffer pool，移入prepared queue
    if len(buffer_pool) != 0:
        package = buffer_pool[0]
        last_log_time, loc, event = package.read_Log() # processing 日志
        if time_now - last_log_time >= time_tick:
            for i in buffer_pool:
                station.remove_buffer(i)
                station.prepared_queue.append(i)
    # 若buffer pool为空
    # 将queue中包裹移入buffer pool
    # 增加process log
    if len(buffer_pool) == 0:
        while station.package_queue.size() != 0:
            packages_queue = station.package_queue.pop(station)
            for package in packages_queue:
                station.add_buffer(package)
                Add_Log_Processing(package, t, station.ind)
"""


"""
def Station_Process(stations, time_begin, time_tick = 1): # 更新所有站点的处理状态
    for i in range(len(stations)):
        Queue_Buffer(stations[i], time_begin, time_tick=time_tick)

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
"""



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


"""
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
    time_begin = time.time()
    simulation_time = 40
    time_tick = 1
    while time.time() - time_begin <= simulation_time/time_tick:
        for package in Packages:
            if not package.Arrive:
                Package_Process(package=package, stations=Stations,routes=Paths[package.ind], time_begin=time_begin, Time_Graph=TimeGraph, Cost_Graph=CostGraph, time_tick=time_tick)
                # Station_Process(Stations, time_begin, time_tick=time_tick)
        Station_Process(Stations, time_begin, time_tick=time_tick)
        # It should be verified whether the Station_Process should be in the loop or out the loop
        # out the loop 误差更小
    while input("Do you want to check the package info? (y/n): ") != "n":
        i = int(input("Input the index of the package you want to check: "))
        print("The package information is as follows: ")
        print("Package Log: ", Packages[i].Log)
        print("Package Path:", Paths[i])
        Packages[i].info()
        if Packages[i].Arrive:
            real_time, real_cost = Packages[i].TimeC,0
            for s in range(len(Paths[i])-1):
                real_time += Stations[Paths[i][s]].Delay
                real_time += TimeGraph[Paths[i][s]][Paths[i][s+1]]
                real_cost += Stations[Paths[i][s]].Cost
                real_cost += CostGraph[Paths[i][s]][Paths[i][s+1]]
            print(f"Real Arrived Time: {real_time} "+f" The Difference between real and simulation is {real_time - Packages[i].Arrived_time}")
            print(f"Real Money Cost: {real_cost} "+f" The Difference between real and simulation is {real_cost - Packages[i].Money_cost}")
    print(Paths)
"""


    

            
