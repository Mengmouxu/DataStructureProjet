class PriorityQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, event, time):
        self.queue.append((event, time))
        self.queue.sort(key=lambda x: x[1])
    
    def pop(self):
        if (len(self.queue) == 0):
            return None
        return self.queue.pop(0)

if __name__ == "__main__":
    P = PriorityQueue()
    P.enqueue("Event A", 5.0)
    P.enqueue("Event B", 2.5)
    P.enqueue("Event C", 7.0)
    P.enqueue("Event D", 3.0)
    print(P.queue)
    print(P.pop())
    print(P.pop())
    print(P.pop())
    print(P.pop())
    print(P.pop())
    print(P.queue)




