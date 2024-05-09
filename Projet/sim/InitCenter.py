"""
File: InitCenter.py
Author: Yanxu Meng
Date: 2024/5/7
Description: This file contains the function to initialize the Centers and Stations.
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import All_Centers_Stations
from utils.Name_config import Name_Ind

def InitCenterStation(Name_Ind):
    init_CS = All_Centers_Stations()
    print("Init Centers and Stations Successfully!")
    return init_CS

if __name__ == "__main__":
    Name_Ind = Name_Ind()
    CS = InitCenterStation(Name_Ind)
