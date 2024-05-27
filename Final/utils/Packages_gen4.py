"""
5/23
"""
import numpy as np
import uuid
import yaml
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

parameters = {
    "station_num": 25,
    "center_num": 5,
    "packet_num": 10000,
}

def clear_yaml(yaml_path):
    with open(''.join(["config/", yaml_path, ".yaml"]), encoding="utf-8", mode="w") as f:
        f.truncate()
def write_yaml(data, yaml_path):
    with open(''.join(["config/", yaml_path, ".yaml"]), encoding="utf-8", mode="a") as f:
        yaml.dump(data, stream=f, allow_unicode=True)
def uuid_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))

def pack_gen():
    packets = []
    src_prob = np.random.random(parameters["station_num"])
    src_prob = src_prob / np.sum(src_prob)
    dst_prob = np.random.random(parameters["station_num"])
    dst_prob = dst_prob / np.sum(dst_prob)
    # Package categories are defined here: 0 for Regular, 1 for Express
    speed_prob = [0.7, 0.3]
    # print("Packets:")
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
    #for packet in packets:
    #    print(uuid.uuid4(), packet)
    return packets

def packages_gen():
    yaml.add_representer(uuid.UUID, uuid_representer)
    pack_dict = dict()
    packages = pack_gen()
    num = len(packages)
    for i in range(num):
        pack_info  = {
            "Category": packages[i][3],
            "Dst": packages[i][2],
            "ID": uuid.uuid4(),
            "Src": packages[i][1],
            "TimeC": packages[i][0],
        }
        pack_dict[i] = pack_info
    clear_yaml("packages4")
    write_yaml(pack_dict, "packages4")



if __name__ == '__main__':
    packages_gen()
