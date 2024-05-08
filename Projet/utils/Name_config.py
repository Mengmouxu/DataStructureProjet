import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.Get_config as cfg
from data.ConfigData import All_Centers_Stations

def Name_Ind():
    CS = All_Centers_Stations()
    Name_Ind = {CS[i].ID: i for i in range(len(CS))}
    return Name_Ind

def Ind_Name():
    CS = All_Centers_Stations()
    Ind_Name = {i: CS[i].ID for i in range(len(CS))}
    return Ind_Name

