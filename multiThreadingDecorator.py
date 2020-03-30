
import time
import threading
import math
import queue


def multithreadFunction(maxNumberOfWorkers):
    # This outer layer provides a parameter to the actual decorator.
    # <maxNumberOfWorkers> : The max number of threads that will be created.

    def _multithreadFunction(originalFunction):
        # This decorator multithreads <originalFunction> .
        # <originalFunction> needs to receive a [list] of tasks to be done as its first argument and return a [list] of solutions.
        # Multithreading steps :
        #     1. Split the list in n sublists ;
        #     2. Create n threads, each computing <originalFunction> on one sublist ;
        #     3. Wait for all threads to be finished ;
        #     4. Fuse the results of all threads and return the full result.

        def _workerFunction(originalFunction, subList, queue, workerNumber, *args, **kwargs):
            # A worker executes the original function on a sublist of tasks and returns the results.
            originalArgs = (subList, *args)
            result = originalFunction(*originalArgs, **kwargs)
            queue.put((workerNumber, result)) # <workerNumber> is used to sort the results
            return

        def _multithreadedFunction(*args, **kwargs):

            assert len(args) > 0, "Multithreaded function received no argument, at least the list of tasks to be performed is required."
            assert isinstance(args[0], list), "Multithreaded function did not receive a list as its first argument. A list of tasks needs to be provided as the first argument."

            fullList = args[0] # The original list of tasks to be splitted
            numberOfWorkers = min(maxNumberOfWorkers, len(fullList)) # At most one worker per task
            _queue = queue.Queue()

            workers = []
            for workerNumber in range(numberOfWorkers):
                workerList = fullList[math.floor(workerNumber * len(fullList) / numberOfWorkers) : math.floor((workerNumber + 1) * len(fullList) / numberOfWorkers)]
                arguments = (originalFunction, workerList, _queue, workerNumber, *(args[1:]))
                kwarguments = kwargs
                worker = threading.Thread(target=_workerFunction, args=(arguments), kwargs=(kwarguments))
                workers.append(worker)

            for worker in workers:
                worker.start()

            for worker in workers:
                worker.join() # Waiting for all workers to be finished

            workerResults = []
            while not _queue.empty():
                workerResult = _queue.get() # Reading partial results from all workers
                workerResults.append(workerResult)

            results = []
            workerResults.sort(key=lambda x:x[0]) # Sorting the partial results
            for workerResult in workerResults:
                results.extend(workerResult[1]) # Fusing all partial results in order

            return results
        return _multithreadedFunction
    return _multithreadFunction


if (__name__ == "__main__"):

    myList = list(range(20))

    # @multiThreadFunction
    def computeSquares(listToSquare, initialValue, endMessage=''):
        results = []
        for elt in listToSquare:
            results.append(elt*elt + initialValue)
            time.sleep(0.1) # Simulating a long task to solve
        print(endMessage)
        return results

    nbIterations = 10
    before = time.time()
    for _ in range(nbIterations):
        val = computeSquares(list(range(20)), 4, endMessage="I'm done compting")
        print(val)
    after = time.time()
    print(f"{(after - before) / nbIterations}s average over {nbIterations} samples")



