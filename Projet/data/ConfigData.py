import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.Get_config as cfg

class center:
    def __init__(self, id, centers = cfg.get_centers()):
        self.ind, self.ID, self.Pos, self.Throughput, self.Delay, self.Cost = self.load_data_from_config(id, centers)
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
        print( )

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
        print( )

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
    def __init__(self, id, packages = cfg.get_packages()):
        self.ind = id
        self.ID, self.Time, self.Src, self.Dst, self.Category = self.load_data_from_config(id, packages)
    def load_data_from_config(self, id, packages):
        if type(id) == int and id in packages:
            package_data = packages[id]
            return package_data["ID"], package_data["Time"], package_data["Src"], package_data["Dst"], package_data["Category"]
    def info(self):
        print(f"Index of this Package is {self.ind}")
        print(f"> Package ID: {self.ID}")
        print(f"> Package Time Created: {self.Time}")
        print(f"> Package Source: {self.Src}")
        print(f"> Package Destination: {self.Dst}")
        print(f"> Package Category: {self.Category}")
        print( )

def All_Packages():
    packages = cfg.get_packages()
    Packages = []
    for i in range(cfg.len_packages()):
        p = package(i, packages)
        Packages.append(p)
    return Packages

if __name__ == "__main__":
    print(Routes_Graph())
    for i in range(len(All_Centers_Stations())):
        All_Centers_Stations()[i].info()
    for i in range(10):
        package(i).info()