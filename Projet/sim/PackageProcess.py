import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import All_Centers_Stations, All_Packages, Routes_Graph
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


def Timeline(package, routes):
    Passed_station = set()
    if package.read_Log() != None:
        Log = package.Log
        for log in Log:
            Passed_station.add(log["Location"])
    for i in range(len(routes)):
        Passed_station.add(routes[i])
    Timeline = list(Passed_station)
    return Timeline


def Package_Process(package, stations, routes,\
                    time_begin, Time_Graph, Cost_Graph):
    """
    Here, the i represents the index of the package in the Packages
    routes represents the sations of the package will pass
    sations represents the information of all the centers and stations
    """
    time_now = time.time()
    t = (time_now - time_begin) * 1
    if package.read_Log() == None and t >= package.TimeC:
        Add_Log_Arrived(package, t, package.Src)
        stations[package.Src].package_queue.enqueue(package)
        return
    if package.read_Log() != None:
        last_time, last_pos, last_event = package.read_Log()
        past_time = t - last_time
        last_ind = routes.index(last_pos)
        if last_ind == len(routes) - 1:
            return
        next_station = routes[ last_ind+ 1]
        if last_event == 1:
            if past_time >= stations[last_pos].Delay:
                Add_Log_Sent(package, last_time + stations[last_pos].Delay, last_pos)
                stations[last_pos].remove_buffer(package)
            if past_time >= stations[last_pos].Delay + Time_Graph[last_pos][next_station]:
                Add_Log_Arrived(package, last_time + stations[last_pos].Delay + Time_Graph[last_pos][next_station], next_station)
                if not package.Dst == next_station:
                    stations[next_station].package_queue.enqueue(package)
        if last_event == 2:
            if past_time >= Time_Graph[last_pos][next_station]:
                Add_Log_Arrived(package, last_time + Time_Graph[last_pos][next_station], next_station)
                if not package.Dst == next_station:
                    stations[next_station].package_queue.enqueue(package)
        
def Queue_Buffer(station, time_begin):
    time_now = time.time()
    t = (time_now - time_begin) * 1
    while station.package_queue.size() != 0:
        package = station.package_queue.pop()
        station.add_buffer(package)
        Add_Log_Processing(package, t, station.ind)

def Station_Process(stations, time_begin):
    for i in range(len(stations)):
        Queue_Buffer(stations[i], time_begin)

def dijkstra(TimeGraph, package):
    src, dst = package.Src, package.Dst
    distances = [float('inf')] * len(TimeGraph)
    visited = [False] * len(TimeGraph)
    distances[src] = 0
    prev = [-1] * len(TimeGraph)  # Add this line to initialize prev

    for _ in range(len(TimeGraph)):
        min_dist = float('inf')
        min_dist_vertex = -1
        for v in range(len(TimeGraph)):
            if not visited[v] and distances[v] < min_dist:
                min_dist = distances[v]
                min_dist_vertex = v
        visited[min_dist_vertex] = True
        for v in range(len(TimeGraph)):
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

# Example usage:

if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Stations = InitCenterStation(Name_Ind)
    Packages = Init_packageLog(Name_Ind)
    TimeGraph, CostGraph = Routes_Graph()
    num = 0
    Paths = [dijkstra(TimeGraph, package=Packages[i]) for i in range(len(Packages))]
    time_begin = time.time()
    while time.time() - time_begin <= 40:
        for i in range(len(Packages)):
            Package_Process(Packages[i],Stations,Paths[i], time_begin=time_begin, Time_Graph=TimeGraph, Cost_Graph=CostGraph)
            Station_Process(Stations, time_begin)
            num += 1
    print(num)
    print(Packages[210].Log)
    Packages[210].info()
