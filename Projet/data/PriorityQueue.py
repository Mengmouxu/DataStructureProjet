"""
File: PriorityQueue.py
Author: Yanxu Meng
Date: 2024/5/5
Description: This file contains the implementation of a Priority Queue data structure.
"""

# from ConfigData import All_Packages

class PriorityQueue:
    """
    A queue for the storage of packages' information
    with functions: enqueue() and pop()
    you could use info() to get the ID of packages in queue
    """
    def __init__(self):
        self.queue = []

    def enqueue(self, package):
        self.queue.append(package)
        self.insert_sort_queue()
    
    def pop(self):
        if (len(self.queue) == 0):
            return None
        return self.queue.pop(0)
    def info(self):
        pack_name = []
        for i in range(len(self.queue)):
            pack_name.append(self.queue[i].ID)
        print(pack_name)
        return pack_name
    def insert_sort_queue(self):
        """
        As this project is a DATA STRUCTURE project,
        I will not write insert sort with my bare hands.
        """
        n = len(self.queue)
        for i in range(1, n):
            key = self.queue[i]
            j = i - 1
            while j >= 0 and self.queue[j].TimeC > key.TimeC:
                self.queue[j + 1] = self.queue[j]
                j -= 1
            self.queue[j + 1] = key
    def size(self):
        return len(self.queue)


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