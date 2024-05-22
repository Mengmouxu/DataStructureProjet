"""
File: PriorityQueue.py
Author: Yanxu Meng
Date: 2024/5/5
Description: This file contains the implementation of a Priority Queue data structure.
"""

# from ConfigData import All_Packages
import math

class PriorityQueue:
    """
    A queue for the storage of packages' information
    with functions: enqueue() and pop()
    you could use info() to get the ID of packages in queue
    """
    waiting_time_limit = 5
    @staticmethod
    def find_queue(queue, cs): # 找到要处理的 throughput 个包裹
        length = len(queue)
        throughput = cs.Throughput
        if length == 0:
            return None
        if length <= throughput:
            return queue
        if length > throughput:
            top_queue = []
            for i in range(throughput):
                top_queue.append(queue[i])
            return top_queue
    def __init__(self):
        self.express_queue = []
        self.normal_queue = []
        self.queue = []
    def enqueue(self, package): # package入库
        self.queue.append(package)
    def pop(self, cs): # 从队列中取出需要处理的包裹，改变queue
        throughput = cs.Throughput
        length = len(self.queue)
        if length == 0:
            return None
        if length <= throughput:
            queue = []
            for i in range(length):
                queue.append(self.queue.pop(0))
            for package in queue:
                package.Waitingtime = 0
            return queue
        if length > throughput:
            queue = []
            for i in range(throughput):
                queue.append(self.queue.pop(0))
            for package in self.queue:
                package.Waitingtime += 1
            return queue
    def info(self):
        pack_name = []
        for i in range(len(self.queue)):
            pack_name.append(self.queue[i].ID)
        print(pack_name)
        return pack_name
    def sort_queue(self): # 所有包裹一视同仁按TimeC排序，改变queue
        nor_queue = self.normal_queue
        exp_queue = self.express_queue
        nor_queue.sort(key = lambda package: package.TimeC)
        exp_queue.sort(key = lambda package: package.TimeC)
        self.queue = exp_queue + nor_queue
        return self.queue
    """
    def find_queue(self, cs):
        length = len(self.queue)
        throughput = cs.Throughput
        if length == 0:
            return None
        if length <= throughput:
            queue = []
            for i in range(length):
                queue.append(self.queue[i])
            return queue
        if length > throughput:
            queue = []
            for i in range(throughput):
                queue.append(self.queue[i])
            return queue
    """
    def prior_normal(self): # 普快中因超时而需优先处理
        nor_queue = self.normal_queue
        prior_nor_queue = []
        for package in nor_queue:
            if package.Waitingtime > self.waiting_time_limit:
                prior_nor_queue.append(package)
        return prior_nor_queue

    def prior_sort(self): # 优先处理超时普快，改变queue
        prior_nor_queue = self.prior_normal()
        self.queue = prior_nor_queue + self.express_queue + self.normal_queue[len(prior_nor_queue):]
        return self.queue
    """
    def insert_sort_queue(self):
        n = len(self.queue)
        for i in range(1, n):
            key = self.queue[i]
            j = i - 1
            while j >= 0 and self.queue[j].TimeC > key.TimeC:
                self.queue[j + 1] = self.queue[j]
                j -= 1
            self.queue[j + 1] = key
    """
    def size(self):
        return len(self.queue)
    
    """
    def queue_wait_time(self, cs): # 队列的等待时间，向上取整

        throughput = cs.Throughput
        length = len(self.queue)
        wait_time = math.ceil(length / throughput)
        return wait_time
    """
    


# due to the circular import, this test will not be accessed.

# if __name__ == "__main__":
#     P = PriorityQueue()
#     pk = All_Packages()
#     P.enqueue(pk[800])
#     P.enqueue(pk[200])
#     P.enqueue(pk[300])
#     P.enqueue(pk[50])
#     P.info()
#     P.pop().info()
#     P.pop().info()
#     P.pop().info()
#     P.pop().info()
#     print(P.queue)
#     for i in range(1000):
#         P.enqueue(pk[i])