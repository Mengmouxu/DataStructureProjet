from ConfigData import package
from utils.Get_config import get_packages,write_yaml, clear_yaml, read_yaml_all

class packageLog(package):
    def __init__(self, id, packages=get_packages()):
        super().__init__(id, packages)
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

def Init_packageLog():
    """
    Init the packageLog list with all packages at the beginning of simulation.
    """
    packages = get_packages()
    PL = []
    for i in range(len(packages)):
        PL.append(packageLog(i, packages))
    return PL

def Load_packageLog(Log):
    """
    Load the packageLog list into the yaml file.
    """
    clear_yaml("packagetrack")
    Log_loadin = {}
    for i in range(len(Log)):
        Log_loadin[Log[i].ind] = {
            "Log": Log[i].Log,
            "ID": Log[i].ID,
            "Src": Log[i].Src,
            "Dst": Log[i].Dst,
            "TimeC": Log[i].TimeC,
            "Category": Log[i].Category
        }
    write_yaml(Log_loadin, "packagetrack")

def Read_packageLog():
    """
    Read the packageLog list from the yaml file.
    """
    packageLogs = read_yaml_all("packagetrack")
    PL = Init_packageLog()
    for i in range(len(PL)):
        PL[i].Log = packageLogs[i]["Log"]
    return PL

if __name__ == "__main__":
    PL = Init_packageLog()
    PL[100].info()
    PL[100].add_Log(10, [12, 2], 2)
    print(PL[100].read_Log())
    PL[100].add_Log(12, [12, 2], 1)
    print(PL[100].read_Log())
    print(PL[100].Log)
    Load_packageLog(PL)
    PL_r = Read_packageLog()
    print(PL_r[100].read_Log())
    print(PL_r[100].pop_Log())
    print(PL_r[100].read_Log())
