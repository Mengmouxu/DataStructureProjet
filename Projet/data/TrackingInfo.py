"""
File: TrackingInfo.py
Author: Yanxu Meng
Date: 2024/5/7
Description: This file contains classes and fuunctions for tracking the packages.
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import package
from utils.Get_config import get_packages,write_yaml, clear_yaml, read_yaml_all
from utils.Name_config import Ind_Name, Name_Ind

class packageLog(package):
    def __init__(self, id, Ind_Name, packages=get_packages()):
        super().__init__(id, Ind_Name, packages)
        self.Log = []
    def add_Log(self, time, location, event):
        """
        event = 0 -> ARRIVED \\
        event = 1 -> PROCESSING \\
        event = 2 -> SENT \\
        events = ["ARRIVED", "PROCESSING", "SENT"]
        """
        events = ["ARRIVED", "PROCESSING", "SENT"]
        event_log = {
            "Time": time,
            "Location": location,
            "Event": events[event]
        }
        self.Log.append(event_log)
    
    def read_Log(self, index = -1):
        """
        event = 0 -> ARRIVED \\
        event = 1 -> PROCESSING \\
        event = 2 -> SENT \\
        events = ["ARRIVED", "PROCESSING", "SENT"]
        """
        if len(self.Log) == 0:
            return None
        last_log = self.Log[index]
        events = ["ARRIVED", "PROCESSING", "SENT"]
        return last_log["Time"], last_log["Location"], events.index(last_log["Event"])
    
    def pop_Log(self):
        """
        event = 0 -> ARRIVED \\
        event = 1 -> PROCESSING \\
        event = 2 -> SENT \\
        events = ["ARRIVED", "PROCESSING", "SENT"]
        """
        if len(self.Log) == 0:
            return None
        last_log = self.Log.pop(-1)
        events = ["ARRIVED", "PROCESSING", "SENT"]
        return last_log["Time"], last_log["Location"], events.index(last_log["Event"])

def Init_packageLog(Name_Ind):
    """
    Init the packageLog list with all packages at the beginning of simulation.
    """
    packages = get_packages()
    PL = []
    for i in range(len(packages)):
        pl = packageLog(i, Name_Ind, packages)
        PL.append(pl)
    print("Init packageLog list successfully!")
    return PL

def Load_packageLog(Log, Ind_Name):
    """
    Load the packageLog list into the yaml file.
    """
    clear_yaml("packagetrack")
    Log_loadin = {}
    for i in range(len(Log)):
        Log_str = []
        for j in range(len(Log[i].Log)):
            l = Log[i].Log[j]
            l["Location"] = Ind_Name[l["Location"]]
            Log_str.append(l)
        Log_loadin[Log[i].ind] = {
            "Log": Log_str,
            "ID": Log[i].ID,
            "Src": Log[i].Src_n,
            "Dst": Log[i].Dst_n,
            "TimeC": Log[i].TimeC,
            "Category": Log[i].Category
        }
    write_yaml(Log_loadin, "packagetrack")

def Read_packageLog(Name_Ind):
    """
    Read the packageLog list from the yaml file.
    """
    packageLogs = read_yaml_all("packagetrack")
    PL = Init_packageLog(Name_Ind)
    for i in range(len(PL)):
        for j in range(len(packageLogs[i]["Log"])):
            l = packageLogs[i]["Log"][j]
            l["Location"] = Name_Ind[l["Location"]]
            PL[i].Log.append(l)
    return PL

if __name__ == "__main__":
    Name_Ind = Name_Ind()
    Ind_Name = Ind_Name()
    PL = Init_packageLog(Name_Ind)
    PL[100].info()
    PL[100].add_Log(10, 0, 2)
    print(PL[100].read_Log())
    PL[100].add_Log(12, 2, 1)
    print(PL[100].read_Log())
    print(PL[100].Log)
    Load_packageLog(PL, Ind_Name)
    PL_r = Read_packageLog(Name_Ind)
    print(PL_r[100].read_Log())
    print(PL_r[100].pop_Log())
    print(PL_r[100].read_Log())
