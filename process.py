__author__ = 'Jonas'
import threading
import multiprocessing
import JTSv2.datamanage as datamanage
import time


def _execute_background(bg_com, translated_string):

    compiled_input = compile(translated_string, '<string>', 'exec')
    exec(compiled_input)


class Process:

    def __init__(self, execution_statement, data_nexus):
        # initializing the super class

        self.output_queue = multiprocessing.Queue()
        self.com = datamanage.BackgroundShellCom(data_nexus, self.output_queue)
        self.process = multiprocessing.Process(target=_execute_background, args=(self.com, execution_statement,))
        self.process.start()

    def get_exitcode(self):
        return self.process.exitcode

    def is_alive(self):
        return self.process.is_alive()

    def get_return(self):
        return self.output_queue.get(block=True)


# TODO: Implement priority garbage collecting behaviour as Thread
# TODO: Make it contain Programs as well as commands
# TODO: change the request list to a stack containing request objects; register the data nexus as a field
class ProcessList(threading.Thread):

    def __init__(self):
        super(ProcessList, self).__init__()
        # name:Process object
        self.processes = {}
        self.process_starting_request = []

    def append(self, name, process):
        for i in range(0, 100):
            indexed_name = ''.join([name, str(i)])
            if not(indexed_name in self.processes.values()):
                self.processes[indexed_name] = process
                break

    def run(self):
        while True:
            time.sleep(0.001)
            if len(self.process_starting_request) != 0:
                request_list = self.process_starting_request.pop(0)
                self.append(request_list[0], Process(request_list[1], request_list[2]))

    def start_process(self, execution_statement, data_nexus):
        self.process_starting_request.append(["Process", execution_statement, data_nexus])


class Program:
    pass


##########







