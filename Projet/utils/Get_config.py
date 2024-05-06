import yaml
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_centers():
    with open('config/centers.yaml', 'r', encoding="utf-8") as f:
        centers = yaml.safe_load(f)
    return centers

def get_stations():
    with open('config/stations.yaml', 'r', encoding="utf-8") as f:
        stations = yaml.safe_load(f)
    return stations

def get_routes():
    with open('config/routes.yaml', 'r', encoding="utf-8") as f:
        routes = yaml.safe_load(f)
    return routes

def get_packages():
    with open('config/packages.yaml', 'r',  encoding="utf-8") as f:
        packages = yaml.safe_load(f)
    return packages

def len_centers():
    with open('config/centers.yaml', 'r', encoding="utf-8") as f:
        centers = yaml.safe_load(f)
    return len(centers)

def len_stations():
    with open('config/stations.yaml', 'r', encoding="utf-8") as f:
        stations = yaml.safe_load(f)
    return len(stations)

def len_routes():
    with open('config/routes.yaml', 'r', encoding="utf-8") as f:
        routes = yaml.safe_load(f)
    return len(routes)

def len_packages():
    with open('config/packages.yaml', 'r',  encoding="utf-8") as f:
        packages = yaml.safe_load(f)
    return len(packages)

if __name__ == "__main__":
    print(get_centers())
    print(get_stations())
    print(get_routes())
    print(get_packages())
