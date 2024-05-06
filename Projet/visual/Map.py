import sys
import os
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import data.ConfigData as data

def Draw_Map():
    centers = data.All_Centers()
    stations = data.All_Stations()
    _, TimeGraph = data.Routes_Graph()
    cs = data.All_Centers_Stations()

    plt.axis([-10, 110, -10, 110])
    for i in range(len(centers)):
        plt.scatter(centers[i].Pos[0],centers[i].Pos[1], c="black", s=200, alpha=0.7)
    s_pos_x = []
    s_pos_y = []
    Throughput = []
    for i in range(len(stations)):
        s_pos_x.append(stations[i].Pos[0])
        s_pos_y.append(stations[i].Pos[1])
        Throughput.append(stations[i].Throughput)

    for i in range(len(TimeGraph)):
        for j in range(i, len(TimeGraph)):
            if TimeGraph[i][j] != 0:
                plt.plot([cs[i].Pos[0], cs[j].Pos[0]], [cs[i].Pos[1], cs[j].Pos[1]], 'g--', c = cm.BuGn(TimeGraph[i][j]**2/200))
    plt.scatter(np.array(s_pos_x),np.array(s_pos_y), alpha=0.6, c = np.array(Throughput),s = np.array(Throughput)*5, cmap=cm.OrRd)
    plt.colorbar()
    plt.show()

if __name__=="__main__":
    Draw_Map()