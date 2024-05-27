import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import Routes_Graph
from utils.Name_config import Name_Ind, Ind_Name
from utils.Center_init import InitCenterStation

def get_neighbors(station):
    neighbors = [i for i in range(len(Stations))]
    ind = station.ind
    for i in range(len(Stations)):
        timecost = TimeGraph[ind][i]
        moneycost = CostGraph[ind][i]
        if (timecost == 0 and moneycost == 0):
            neighbors.remove(i)
    return neighbors


if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    Stations = InitCenterStation(Name_Ind)
    CostGraph, TimeGraph = Routes_Graph()
    neighbor_list = []
    for station in Stations:
        neighbor_list.append(get_neighbors(station))
    print(neighbor_list)
