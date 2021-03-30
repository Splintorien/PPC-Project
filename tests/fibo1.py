import sys
from multiprocessing import Process, Array

MEMORY_SIZE = 100

def fibonacci(n, mem):
    mem[0] = 0
    a, b = 0, 1
    i = 0
    while i < n:
        a, b = b, a+b
        mem[i+1] = a
        i += 1          # stopping flag
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("required index argument missing, terminating.", file=sys.stderr)
        sys.exit(1)
        
    try:
        index = int(sys.argv[1])
    except ValueError:
        print("bad index argument: {}, terminating.".format(sys.argv[1]), file=sys.stderr)
        sys.exit(2)
        
    if index < 0:
        print("negative index argument: {}, terminating.".format(index), file=sys.stderr)
        sys.exit(3)
        
    if index > 99:
        print("Not enough memory for index argument: {}, terminating.".format(index), file=sys.stderr)
        sys.exit(4)        
        
    shared_memory = Array('l', MEMORY_SIZE)
       
    child = Process(target=fibonacci, args=(index, shared_memory))
    child.start()
    child.join()

    for x in shared_memory[:]:
        print(x, end=" ")
    print()
    
