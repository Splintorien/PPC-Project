import sys
import random
import threading

pointsInside = 0

def pi(n):
    print("Starting thread:", threading.current_thread().name)
    global pointsInside
    for i in range(n):
        x = -1 + 2 * random.random()
        y = -1 + 2 * random.random()
        if x**2 + y**2 <= 1:
            pointsInside += 1
    print("Ending thread:", threading.current_thread().name)            


if __name__ == "__main__":
    print("Starting thread:", threading.current_thread().name)
    if len(sys.argv) < 2:
        print("required number of points missing, terminating.", file=sys.stderr)
        sys.exit(1)
        
    try:
        points = int(sys.argv[1])
    except ValueError:
        print("bad number of points argument: {}, terminating.".format(sys.argv[1]), file=sys.stderr)
        sys.exit(2)
        
    if points < 0:
        print("negative number of points argument: {}, terminating.".format(points), file=sys.stderr)
        sys.exit(3)
    
    thread = threading.Thread(target=pi, args=(points,))
    thread.start()
    thread.join()
    
    print("estimation of pi:", 4 * pointsInside / points)
    print("Ending thread:", threading.current_thread().name)
    









