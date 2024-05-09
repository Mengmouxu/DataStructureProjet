"""
File: Config_data.py
Author: Yanxu Meng
Date: 2024/5/6
Description: This file contains classes accessing to the informations of these data types.
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.Get_config as cfg
from data.PriorityQueue import PriorityQueue

class center:
    def __init__(self, id, centers = cfg.get_centers()):
        self.ind, self.ID, self.Pos, self.Throughput, self.Delay, self.Cost = self.load_data_from_config(id, centers)
        self.package_queue = PriorityQueue()
        self.buffer = []
    def load_data_from_config(self, id, centers):
        if type(id) == int and id in centers:
            center_data = centers[id]
            return id, center_data["ID"], center_data["Pos"], center_data["Throughput"], center_data["Delay"], center_data["Cost"]
        if id.startswith("c") and id[1:].isdigit():
            center_data = {}
            ind = 0
            for i, center in centers.items():
                if center["ID"] == id:
                    center_data = center
                    ind = i
                    break
            return ind, center_data["ID"], center_data["Pos"], center_data["Throughput"], center_data["Delay"], center_data["Cost"]
    def info(self):
        print(f"Index of this Center is {self.ind}")
        print(f"> Center ID: {self.ID}")
        print(f"> Center Position: {self.Pos}")
        print(f"> Center Throughput: {self.Throughput}")
        print(f"> Center Delay: {self.Delay}")
        print(f"> Center Packages number: {self.package_queue.size()}")
        print( )
    def add_buffer(self, package):
        self.buffer.append(package)
    def remove_buffer(self, package):
        self.buffer.remove(package)

def All_Centers():
    centers = cfg.get_centers()
    Center = []
    for i in range(cfg.len_centers()):
        c = center(i, centers)
        Center.append(c)
    return Center

class station:
    def __init__(self, id, stations = cfg.get_stations()):
        self.ind, self.ID, self.Pos, self.Throughput, self.Delay, self.Cost = self.load_data_from_config(id, stations)
        self.ind += cfg.len_centers()
        self.package_queue = PriorityQueue()
        self.buffer = []
    def load_data_from_config(self, id, stations):
        if type(id) == int and id in stations:
            station_data = stations[id]
            return id, station_data["ID"], station_data["Pos"], station_data["Throughput"], station_data["Delay"], station_data["Cost"]
        if id.startswith("s") and id[1:].isdigit():
            station_data = {}
            ind = 0
            for i,station in stations.items():
                if station["ID"] == id:
                    station_data = station
                    ind = i
            return ind, station_data["ID"], station_data["Pos"], station_data["Throughput"], station_data["Delay"], station_data["Cost"]
    def info(self):
        print(f"Index of this Station is {self.ind}")
        print(f"> Station ID: {self.ID}")
        print(f"> Station Position: {self.Pos}")
        print(f"> Station Throughput: {self.Throughput}")
        print(f"> Station Delay: {self.Delay}")
        print(f"> Station Packages number: {self.package_queue.size()}")
        print( )
    def add_buffer(self, package):
        self.buffer.append(package)
    def remove_buffer(self, package):
        self.buffer.remove(package)

def All_Stations():
    stations = cfg.get_stations()
    Station = []
    for i in range(cfg.len_stations()):
        s = station(i, stations)
        Station.append(s)
    return Station

def find_route(src, dst):
    s,d = 0,0
    if src[0] == "s":
        st = station(src)
        s = st.ind
    if src[0] == "c":
        ct = center(src)
        s = ct.ind
    if dst[0] == "s":
        st = station(dst)
        d = st.ind
    if dst[0] == "c":
        ct = center(dst)
        d = ct.ind
    return s, d

class route():
    def __init__(self, id, routes = cfg.get_routes()):
        self.ind, self.Src, self.Dst, self.Cost, self.Time = self.load_data_from_config(id, routes)
        self.On_route = []
    def load_data_from_config(self, id, routes):
        if type(id) == int and id in routes:
            route_data = routes[id]
            return id, route_data["Src"], route_data["Dst"], route_data["Cost"], route_data["Time"]
    def info(self):
        print(f"Index of this Route is {self.ind}")
        print(f"> Route Source: {self.Src}")
        print(f"> Route Destination: {self.Dst}")
        print(f"> Route Cost: {self.Cost}")
        print(f"> Route Time: {self.Time}")
        print( )
    def add_package(self, package):
        self.On_route.append(package)
    def remove_package(self, package):
        self.On_route.remove(package)

def Init_Routes():
    routes = cfg.get_routes()
    Route = []
    for i in range(cfg.len_routes()):
        r = route(i, routes)
        Route.append(r)
    return Route

def Routes_Graph():
    n_center = cfg.len_centers()
    n_station = cfg.len_stations()
    n_sum = n_station + n_center
    CostGraph = []
    TimeGraph = []
    for i in range(n_sum):
        l = [0] * n_sum
        CostGraph.append(l)
        TimeGraph.append(l)
    route_data = cfg.get_routes()
    for ind, route in route_data.items():
        s, d = find_route(route["Src"], route["Dst"])
        CostGraph[s][d] = route["Cost"]
        TimeGraph[s][d] = route["Time"]
    return CostGraph, TimeGraph

def All_Centers_Stations():
    return All_Centers() + All_Stations()

class package:
    def __init__(self, id, cs_name, packages = cfg.get_packages()):
        self.ind = id
        self.ID, self.TimeC, self.Src, self.Dst, self.Category, self.Src_n, self.Dst_n = self.load_data_from_config(id, cs_name, packages)
        self.t = 0
        self.m = 0
        # Init the time cost and money cost of the package
    def load_data_from_config(self, id,cs_name, packages):
        if type(id) == int and id in packages:
            package_data = packages[id]
            return package_data["ID"], package_data["TimeC"], cs_name[package_data["Src"]], cs_name[package_data["Dst"]], package_data["Category"], package_data["Src"], package_data["Dst"]
    def info(self):
        print(f"Index of this Package is {self.ind}")
        print(f"> Package ID: {self.ID}")
        print(f"> Package Time Created: {self.TimeC}")
        print(f"> Package Source: {self.Src_n}")
        print(f"> Package Destination: {self.Dst_n}")
        print(f"> Package Category: {self.Category}")
        print( )

def All_Packages():
    packages = cfg.get_packages()
    CS = All_Centers_Stations()
    CS_name = {CS[i].ID : i for i in range(len(CS))}
    print(CS_name)
    Packages = []
    for i in range(cfg.len_packages()):
        p = package(i, CS_name, packages)
        Packages.append(p)
    return Packages

if __name__ == "__main__":
    print(Routes_Graph())
    cs = All_Centers_Stations()
    pk = All_Packages()
    for i in range(len(cs)):
        cs[i].info()
    for i in range(1000):
        pk[i].info()
    rt = Init_Routes()
    for i in range(len(rt)):
        rt[i].info()