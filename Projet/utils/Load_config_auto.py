import yaml
import sys
import random
import numpy as np
import matplotlib.pyplot as plt
import uuid
from sklearn.cluster import KMeans
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def read_yaml_all(yaml_path):
    with open(''.join(["config/", yaml_path, ".yaml"]), "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data

def write_yaml(data, yaml_path):
    with open(''.join(["config/", yaml_path, ".yaml"]), encoding="utf-8", mode="a") as f:
        yaml.dump(data, stream=f, allow_unicode=True)

def clear_yaml(yaml_path):
    with open(''.join(["config/", yaml_path, ".yaml"]), encoding="utf-8", mode="w") as f:
        f.truncate()


def set_parameters():
    parameters = {}
    while True:
        s_n = input("Enter the number of Stations (integer): ")
        if s_n.isdigit() and int(s_n) > 0:
            parameters["station_num"] = int(s_n)
            break
        else:
            print("Invalid input. Please enter an integer greater than 0.")
            continue
    while True:
        c_n = input("Enter the number of Centers (integer): ")
        if c_n.isdigit() and int(c_n) > 0:
            parameters["center_num"] = int(c_n)
            break
        else:
            print("Invalid input. Please enter an integer greater than 0.")
            continue
    while True:
        p_n = input("Enter the number of Packages (integer): ")
        if p_n.isdigit() and int(p_n) > 0:
            parameters["packet_num"] = int(p_n)
            break
        else:
            print("Invalid input. Please enter an integer greater than 0.")
            continue
    with open('config/parameters.yaml', 'w') as f:
        yaml.safe_dump(parameters, f)
    print("Load This Center Successfully!")

def data_gen():
    clear_yaml("parameters")
    clear_yaml("stations")
    clear_yaml("centers")
    clear_yaml("routes")
    clear_yaml("packages")
    set_parameters()
    with open('config/parameters.yaml', 'r', encoding="utf-8") as f:
        parameters = yaml.safe_load(f)

    # Generate Stations
    station_pos = []
    # properties are defined here: throughput/tick, time_delay, money_cost
    station_prop_candidates = [
        (10, 2, 0.5), (15, 2, 0.6), (20, 1, 0.8), (25, 1, 0.9)]
    station_prop = []
    for i in range(parameters["station_num"]):
        # Map size is defined here, which is 100*100
        station_pos.append((random.randint(0, 100), random.randint(0, 100)))
        station_prop.append(
            station_prop_candidates[random.randint(0, len(station_prop_candidates)-1)])
    # Output Stations
    print("Stations:")
    for i in range(len(station_pos)):
        print(f"s{i}", station_pos[i], station_prop[i])

    # Generate Centers by clustering
    kmeans = KMeans(n_clusters=parameters["center_num"])
    kmeans.fit(station_pos)
    station_labels = kmeans.predict(station_pos)
    center_pos = [(int(x[0]), int(x[1])) for x in kmeans.cluster_centers_]
    for i in range(len(center_pos)):
        while center_pos[i] in station_pos:
            # move slightly if center is overlapped with station
            # you can also use other methods to avoid this situation
            print("Warning: Center moved")
            center_pos[i] = center_pos[i][0] + 1, center_pos[i][1] + 1
    # properties are defined here: throughput/tick, time_delay, money_cost
    center_prop_candidates = [
        (100, 2, 0.5), (150, 2, 0.5), (125, 1, 0.5), (175, 1, 0.5)]
    center_prop = []
    for i in range(parameters["center_num"]):
        center_prop.append(
            center_prop_candidates[random.randint(0, len(center_prop_candidates)-1)])
    # Output Centers
    print("Centers:")
    for i in range(parameters["center_num"]):
        print(f"c{i}", center_pos[i], center_prop[i])

    # Draw Stations and Centers
    plt.scatter([x[0] for x in station_pos], [x[1]
                for x in station_pos], c=station_labels, s=50, cmap='viridis')
    plt.scatter([x[0] for x in center_pos], [x[1]
                for x in center_pos], c='black', s=200, alpha=0.5)

    # Generate Edges
    edges = []
    print("Edges (center to center):")      # Airlines
    for i in range(parameters["center_num"]):
        for j in range(parameters["center_num"]):
            if j > i:
                dist = np.linalg.norm(
                    np.array(center_pos[i]) - np.array(center_pos[j]))
                # src, dst, time_cost, money_cost
                # time_cost and money_cost are defined here
                edges.append((f"c{i}", f"c{j}", 0.25 * dist, 0.2 * dist))
                edges.append((f"c{j}", f"c{i}", 0.25 * dist, 0.2 * dist))
                plt.plot([center_pos[i][0], center_pos[j][0]], [
                         center_pos[i][1], center_pos[j][1]], 'r--')
                print(edges[-2])
                print(edges[-1])
    print("Edges (center to station):")     # Highways
    for i in range(parameters["center_num"]):
        for j in range(parameters["station_num"]):
            if station_labels[j] == i:
                dist = np.linalg.norm(
                    np.array(center_pos[i]) - np.array(station_pos[j]))
                # time_cost and money_cost are defined here
                edges.append((f"c{i}", f"s{j}", 0.6 * dist, 0.12 * dist))
                edges.append((f"s{j}", f"c{i}", 0.6 * dist, 0.12 * dist))
                plt.plot([center_pos[i][0], station_pos[j][0]], [
                         center_pos[i][1], station_pos[j][1]], 'b--')
                print(edges[-2])
                print(edges[-1])
    print("Edges (station to station):")    # Roads
    for i in range(parameters["station_num"]):
        for j in range(parameters["station_num"]):
            if i > j and (np.linalg.norm(np.array(station_pos[i]) - np.array(station_pos[j])) < 30):
                dist = np.linalg.norm(
                    np.array(station_pos[i]) - np.array(station_pos[j]))
                # time_cost and money_cost are defined here
                edges.append((f"s{i}", f"s{j}", 0.8 * dist, 0.07*dist))
                edges.append((f"s{j}", f"s{i}", 0.8 * dist, 0.07*dist))
                plt.plot([station_pos[i][0], station_pos[j][0]], [
                         station_pos[i][1], station_pos[j][1]], 'g--')
                print(edges[-2])
                print(edges[-1])
    plt.show()

    # Generate Packets
    packets = []
    src_prob = np.random.random(parameters["station_num"])
    src_prob = src_prob / np.sum(src_prob)
    dst_prob = np.random.random(parameters["station_num"])
    dst_prob = dst_prob / np.sum(dst_prob)
    # Package categories are defined here: 0 for Regular, 1 for Express
    speed_prob = [0.7, 0.3]
    print("Packets:")
    for i in range(parameters["packet_num"]):      # Number of packets
        src = np.random.choice(parameters["station_num"], p=src_prob)
        dst = np.random.choice(parameters["station_num"], p=dst_prob)
        while dst == src:
            dst = np.random.choice(parameters["station_num"], p=dst_prob)
        category = np.random.choice(2, p=speed_prob)
        # Create time of the package, during 12 time ticks(hours). Of course you can change it.
        create_time = np.random.random() * 12
        packets.append((create_time, f"s{src}", f"s{dst}", category))
    # Sort packets by create time
    packets.sort(key=lambda x: x[0])
    # Output Packets
    for packet in packets:
        print(uuid.uuid4(), packet)

    return {
        "station_pos": station_pos,
        "station_prop": station_prop,
        "center_pos": center_pos,
        "center_prop": center_prop,
        "edges": edges,
        "packets": packets,
    }

def append_centers_config(center_pos, center_prop):
    center_data = {}
    n_center = len(center_pos)
    for i in range(n_center):
        center_data[i] = {
            "ID": f"c{i}",
            "Pos": [int(center_pos[i][0]), int(center_pos[i][1])],
            "Throughput": center_prop[i][0],
            "Delay": center_prop[i][1],
            "Cost" : center_prop[i][2]
        }
    write_yaml(center_data, "centers")

def append_stations_config(station_pos, station_prop):
    station_data = {}
    n_station = len(station_pos)
    for i in range(n_station):
        station_data[i] = {
            "ID": f"s{i}",
            "Pos": [int(station_pos[i][0]), int(station_pos[i][1])],
            "Throughput": station_prop[i][0],
            "Delay": station_prop[i][1],
            "Cost": station_prop[i][2]
        }
    write_yaml(station_data, "stations")
    
def append_routes_config(edges):
    route_data = {}
    n_route = len(edges)
    for i in range(n_route):
        e = list(edges[i])
        route_data[i] = {
            "Src": str(e[0]),
            "Dst": str(e[1]),
            "Time": float(e[2]),
            "Cost": float(e[3]),
        }
    write_yaml(route_data, "routes")

def append_packages_config(packet):
    packet_data = {}
    for i in range(len(packet)):
        packet_data[i] = {
            "ID": i,
            "Time":float(packet[i][0]),
            "Src":str(packet[i][1]),
            "Dst":str(packet[i][2]),
            "Category":int(packet[i][3]),
        }
    write_yaml(packet_data, "packages")



if __name__ == '__main__':
    data = data_gen()
    append_centers_config(data["center_pos"], data["center_prop"])
    append_stations_config(data["station_pos"], data["station_prop"])
    append_routes_config(data["edges"])
    append_packages_config(data["packets"])