import yaml
import sys
sys.path.append('..')

def show_sc():
    with open('config/centers.yaml', 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
        c = []
        for k in config.keys():
            c.append(config[k]["ID"])
        print(">>> Center ID: ", ' '.join(c))
    with open('config/stations.yaml', 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
        s = []
        for k in config.keys():
            s.append(config[k]["ID"])
        print(">>> Station ID: ", ' '.join(s))


def append_centers_config():
    with open('config/centers.yaml', 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
    Index = 0
    if config == None:
        Index = 0
        config = {}
    else:
        Index = len(config)
    center_data = config
    center_data[Index] = {}
    while True:
        ID = input("> Enter a new center ID (eg: c123) : ")
        exist = False
        for data in config.values():
            if data and 'ID' in data and ID == data['ID']:
                print(f"Center with ID {ID} already exists.")
                exist = True
        if exist:
            continue
        if ID[0] != 'c' or not ID[1:].isdigit():
            print("Invalid center ID format. It should start with 'c' followed by int")
            continue
        else:
            center_data[Index]["ID"] = ID
            break
    while True:
        Pos = input("> Enter the position of the center (eg: 32,25) : ")
        pos = Pos.strip().split(',')
        if len(pos) != 2 and not pos[0].isdigit() or not pos[1].isdigit() \
        or not 0 <= int(pos[0]) <= 100 or not 0 <= int(pos[1]) <= 100:
            print("Invalid position format. It should be two integers within [0, 100] separate with a comma.")
            continue
        else:
            center_data[Index]["Pos"] = [int(pos[0]), int(pos[1])]
            break
    while True:
        Throughput = input("> Enter the throughput of the center (eg: 5) : ")
        if not Throughput.isdigit():
            print("Invalid throughput format. It should be an integer.")
            continue
        else:
            center_data[Index]["Throughput"] = int(Throughput)
            break
    while True:
        Delay = input("> Enter the delay of the center (eg: 2) : ")
        if not Delay.isdigit():
            print("Invalid delay format. It should be an integer.")
            continue
        else:
            center_data[Index]["Delay"] = int(Delay)
            break
    while True:
        Cost = input("> Enter the cost of the center (eg: 10.50) : ")
        if not Cost.replace('.', '').isdigit():
            print("Invalid cost format. It should be a float.")
        else:
            center_data[Index]["Cost"] = float(Cost)
            break
    with open('config/centers.yaml', 'w') as f:
        yaml.safe_dump(center_data, f)
    print("Load This Center Successfully!")


def append_stations_config():
    with open('config/stations.yaml', 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
    Index = 0
    if config == None:
        Index = 0
        config = {}
    else:
        Index = len(config)
    station_data = config
    station_data[Index] = {}
    while True:
        ID = input("> Enter a new station ID (eg: s123) : ")
        exist = False
        for data in config.values():
            if data and 'ID' in data and ID == data["ID"]:
                print(f"Station with ID {ID} already exists.")
                exist = True
        if exist:
            continue
        if ID[0] != 's' or not ID[1:].isdigit():
            print("Invalid station ID format. It should start with 's' followed by int")
            continue
        else:
            station_data[Index]["ID"] = ID
            break
    while True:
        Pos = input("> Enter the position of the station (eg: 32,25) : ")
        pos = Pos.strip().split(',')
        if len(pos) != 2 and not pos[0].isdigit() or not pos[1].isdigit() \
        or not 0 <= int(pos[0]) <= 100 or not 0 <= int(pos[1]) <= 100:
            print("Invalid position format. It should be two integers within [0, 100] separate with a comma.")
            continue
        else:
            station_data[Index]["Pos"] = [int(pos[0]), int(pos[1])]
            break
    while True:
        Throughput = input("> Enter the throughput of the station (eg: 5) : ")
        if not Throughput.isdigit():
            print("Invalid throughput format. It should be an integer.")
            continue
        else:
            station_data[Index]["Throughput"] = int(Throughput)
            break
    while True:
        Delay = input("> Enter the delay of the station (eg: 2) : ")
        if not Delay.isdigit():
            print("Invalid delay format. It should be an integer.")
            continue
        else:
            station_data[Index]["Delay"] = int(Delay)
            break
    while True:
        Cost = input("> Enter the cost of the station (eg: 10.50) : ")
        if not Cost.replace('.', '').isdigit():
            print("Invalid cost format. It should be a float.")
        else:
            station_data[Index]["Cost"] = float(Cost)
            break
    with open('config/stations.yaml', 'w') as f:
        yaml.safe_dump(station_data, f)
    print("Load This Station Successfully!")


def append_routes_config():
    with open('config/routes.yaml', 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
    Index = 0
    if config == None:
        Index = 0
        config = {}
    else:
        Index = len(config)
    route_data = config
    route_data[Index] = {}
    show_sc()
    while True:
        Src = input("> Enter the source ID (eg: c123 or s123) : ")
        if Src[0] != 'c' and Src[0] != 's' or not Src[1:].isdigit():
            print("Invalid source ID format. It should start with 'c' or 's' followed by int")
            continue
        exist = False
        with open('config/stations.yaml', 'r', encoding="utf-8") as f:
            config_s = yaml.safe_load(f)
        for data in config_s.values():
            if Src == data["ID"]:
                exist = True
        with open('config/centers.yaml', 'r', encoding="utf-8") as f:
            config_d = yaml.safe_load(f)
        for data in config_d.values():
            if Src == data["ID"]:
                exist = True
        if exist:
            route_data[Index]["Src"] = Src
            break
        else:
            print("Center or Station with ID {} does not exist.".format(Src))
            continue
    while True:
        Dst = input("> Enter the destination ID (eg: c123 or s123) : ")
        if Dst[0] != 'c' and Dst[0] != 's' or not Dst[1:].isdigit():
            print("Invalid destination ID format. It should start with 'c' or 's' followed by int")
            continue
        exist = False
        with open('config/stations.yaml', 'r', encoding="utf-8") as f:
            config_s = yaml.safe_load(f)
        for data in config_s.values():
            if Dst == data["ID"]:
                exist = True
        with open('config/centers.yaml', 'r', encoding="utf-8") as f:
            config_d = yaml.safe_load(f)
        for data in config_d.values():
            if Dst == data["ID"]:
                exist = True
        if exist and Dst != route_data[Index]["Src"]:
            route_data[Index]["Dst"] = Dst
            break
        if not exist:
            print("Center or Station with ID {} does not exist.".format(Dst))
            continue
        if Dst == route_data[Index]["Src"]:
            print("Destination cannot be the same as the source.")
            continue
    while True:
        Time = input("> Enter the time of the route (eg: 10.5) : ")
        if not Time.replace('.', '').isdigit():
            print("Invalid time format. It should be a float.")
            continue
        else:
            route_data[Index]["Time"] = float(Time)
            break
    while True:
        Cost = input("> Enter the cost of the route (eg: 5.25) : ")
        if not Cost.replace('.', '').isdigit():
            print("Invalid cost format. It should be a float.")
            continue
        else:
            route_data[Index]["Cost"] = float(Cost)
            break
    with open('config/routes.yaml', 'w') as f:
        yaml.safe_dump(route_data, f)
    print("Load This Route Successfully!")


def append_packages_config():
    with open('config/packages.yaml', 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
    Index = 0
    if config == None:
        Index = 0
        config = {}
    else:
        Index = len(config)
    package_data = config
    package_data[Index] = {}
    show_sc()
    while True:
        ID = input("> Enter the package ID : ")
        package_data[Index]["ID"] = ID
        break
    while True:
        TimeCreated = input("> Enter the time created for the package (eg: 10.5) : ")
        if not TimeCreated.replace('.', '').isdigit():
            print("Invalid time format. It should be a float.")
            continue
        else:
            package_data[Index]["TimeCreated"] = float(TimeCreated)
            break
    while True:
        Src = input("> Enter the source ID (eg: c123 or s123) : ")
        if Src[0] != 'c' and Src[0] != 's' or not Src[1:].isdigit():
            print("Invalid source ID format. It should start with 'c' or 's' followed by int")
            continue
        exist = False
        with open('config/stations.yaml', 'r', encoding="utf-8") as f:
            config_s = yaml.safe_load(f)
        for data in config_s.values():
            if Src == data["ID"]:
                exist = True
        with open('config/centers.yaml', 'r', encoding="utf-8") as f:
            config_d = yaml.safe_load(f)
        for data in config_d.values():
            if Src == data["ID"]:
                exist = True
        if exist:
            package_data[Index]["Src"] = Src
            break
        else:
            print("Station or center with ID {} does not exist.".format(Src))
            continue
    while True:
        Dst = input("> Enter the destination ID (eg: c123 or s123) : ")
        if Dst[0] != 'c' and Dst[0] != 's' or not Dst[1:].isdigit():
            print("Invalid destination ID format. It should start with 'c' or 's' followed by int")
            continue
        exist = False
        with open('config/stations.yaml', 'r', encoding="utf-8") as f:
            config_s = yaml.safe_load(f)
        for data in config_s.values():
            if Dst == data["ID"]:
                exist = True
        with open('config/centers.yaml', 'r', encoding="utf-8") as f:
            config_d = yaml.safe_load(f)
        for data in config_d.values():
            if Dst == data["ID"]:
                exist = True
        if exist and Dst != package_data[Index]["Src"]:
            package_data[Index]["Dst"] = Dst
            break
        if not exist:
            print("Station or center with ID {} does not exist.".format(Dst))
            continue
        if Dst == package_data[Index]["Src"]:
            print("Destination cannot be the same as the source.")
            continue
    while True:
        Category = input("> Enter the category of the package (0 or 1) : ")
        if Category not in ['0', '1']:
            print("Invalid category format. It should be either 0 or 1.")
            continue
        else:
            package_data[Index]["Category"] = int(Category)
            break
    with open('config/packages.yaml', 'w') as f:
        yaml.safe_dump(package_data, f)
    print("Load This Package Successfully!")


def continue_add(config_name):
    while True:
        status = input("Do you want to add another {}? (y/n): ".format(config_name))
        if status.lower() == "y":
            print( )
            return True
        elif status.lower() == "n":
            print( )
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def main():
    print("Welcome to the configuration tool!")
    print("Please add the following configurations:")
    while continue_add("centers"):
        append_centers_config()
    while continue_add("stations"):
        append_stations_config()
    while continue_add("routes"):
        append_routes_config()
    while continue_add("packages"):
        append_packages_config()

if __name__ == "__main__":
    main()