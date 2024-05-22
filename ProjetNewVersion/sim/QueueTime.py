"""
File: QueueTime.py
Author: Bingrui Jin
Date: 2024/5/19
Description: This file simulates and records the queue time of centers and stations.
"""
# 不需要日志
# 使用排队规则+dijkstra算法计算不同时段某站点的排队时间
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import Routes_Graph
from data.TrackingInfo import Init_packageLog
from utils.Name_config import Name_Ind, Ind_Name
from sim.InitCenter import InitCenterStation
from sim.PackageProcess import dijkstra_t, dijkstra_c, Package_Process, Station_Process
import time
import math
import threading

def queue_wait_time(cs): # 队列的等待时间，向上取整
        throughput = cs.Throughput
        length = len(cs.package_queue.queue)
        wait_time = math.ceil(length / throughput)
        return wait_time

def calculate_queuetime(stations, begin_time):
     time_now = time.time() - begin_time
     time.sleep(1 - time_now)
     while True:
          for cs in stations:
              cs.queue_time_table.append(queue_wait_time(cs))
          time.sleep(1)


if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Stations = InitCenterStation(Name_Ind)
    Packages = Init_packageLog(Name_Ind)
    TimeGraph, CostGraph = Routes_Graph()
    # 找到所有包裹的路径
    Paths = []
    for i in range(len(Packages)):
        package = Packages[i]
        if package.Category == 0: # 普快，只考虑cost
            Paths.append(dijkstra_c(CostGraph, package))
        if package.Category == 1: # 特快，只考虑time
            Paths.append(dijkstra_t(TimeGraph, package))
    # 考虑时间刻度
    time_begin = time.time()
    simulation_time = 40
    time_tick = 1
    queuetime_thread = threading.Thread(target = calculate_queuetime, args=(Stations, time_begin))
    queuetime_thread.daemon = True
    queuetime_thread.start()
    while time.time() - time_begin <= simulation_time/time_tick:
        for package in Packages:
            if not package.Arrive:
                Package_Process(package=package, stations=Stations,routes=Paths[package.ind], time_begin=time_begin, Time_Graph=TimeGraph, Cost_Graph=CostGraph, time_tick=time_tick)
        Station_Process(Stations, time_begin, time_tick=time_tick)
    for cs in Stations:
         print(cs.queue_time_table)
