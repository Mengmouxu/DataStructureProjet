import csv

def write_csv(data, csv_path):
    with open(''.join(["config/", csv_path, ".csv"]), encoding="utf-8", mode="a") as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            writer.writerow(row)
    print(f"数据已成功写入{csv_path}")

def read_csv(csv_path):
    data = []
    with open(''.join(["config/", csv_path, ".csv"]), encoding="utf-8", mode="r") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    return data