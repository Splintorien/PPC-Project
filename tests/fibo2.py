import sys
from multiprocessing import Process, Manager

def fibonacci(n, lst):
    lst.append(0)
    a, b = 0, 1
    i = 0
    while i < n:
        a, b = b, a+b
        lst.append(a)
        i += 1
    
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
        
    with Manager() as manager:
        lst = manager.list()

        child = Process(target=fibonacci, args=(index, lst))
        child.start()
        child.join()

        print(lst)

    
    

   
