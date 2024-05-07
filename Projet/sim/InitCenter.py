"""
File: InitCenter.py
Author: Yanxu Meng
Date: 2024/5/7
Description: This file contains the function to initialize the Centers and Stations and \
                and put the packages in the corresponding queue.
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ConfigData import All_Centers_Stations, All_Packages

def InitCenterStation():
    init_CS = All_Centers_Stations()
    init_Packages = All_Packages()
    CS_name = [i.ID for i in init_CS]
    for package in init_Packages:
        for i in range(len(CS_name)):
            name = CS_name[i]
            if package.Src == name:
                init_CS[i].package_queue.enqueue(package)
    print("Init Centers and Stations Successfully!")
    return init_CS

if __name__ == "__main__":
    CS = InitCenterStation()
    package_num = 0
    for i in range(len(CS)):
        CS[i].info()
        package_num += CS[i].package_queue.size()
    print("The number of packages in all Centers and Stations is: ",package_num, " = ", len(All_Packages()))
    print("All packages are in the queue of the corresponding Center or Station.")
