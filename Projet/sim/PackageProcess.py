import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import All_Centers_Stations, All_Packages
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


def Package_Process(package, stations, routes, time_begin, Time_Graph, Cost_Graph):
    """
    Here, the i represents the index of the package in the Packages
    routes represents the sations of the package will pass
    sations represents the information of all the centers and stations
    """
    time_now = time.time()
    t = time_now - time_begin
    Timeline = Timeline(package, routes)
    if package.read_Log() == None and t >= package.TimeC:
        Add_Log_Arrived(package, t, routes[0])
        stations[package.Src].enqueue(package)
    


if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Stations = InitCenterStation(Name_Ind)
    Packages = Init_packageLog(Name_Ind)
    time_begin = time.time()
    while time.time() - time_begin <= 10:
        Package_Process(Packages[500],Stations, routes=[29, 30], time_begin=time_begin, Time_Graph=[], Cost_Graph=[])
    