import sys
import random
import statistics
import threading
from queue import Queue


def worker(task_queue, data, data_ready, res_queue):
    data_ready.wait()
    function = task_queue.get()
    res = function(data)
    res_queue.put([function.__name__, res])
    

if __name__ == "__main__":   
    data = []    
    tasks = [min, max, statistics.median, statistics.mean, statistics.stdev]
    
    task_queue = Queue()
    for t in tasks:
        task_queue.put(t)
        
    data_ready = threading.Event()
    res_queue = Queue()
    
    threads = [threading.Thread(target=worker, args=(task_queue, data, data_ready, res_queue)) for i in range(len(tasks))]
    for thread in threads:
        thread.start()
       
    print("Enter a sequence of real numbers, Ctrl+D to end.")
    
    input_str = sys.stdin.read().split()
    for s in input_str:
        try:
            x = float(s)
        except ValueError:
            print("bad number", s)
        else:
            data.append(x)    
        
    data_ready.set()
    for thread in threads:
        thread.join()

    while not res_queue.empty():
        res = res_queue.get()
        print(res)
