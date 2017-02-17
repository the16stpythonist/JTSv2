__author__ = 'Jonas'
import JTSv2.datamanage as datamanage
import JTSv2.translate as translate
import JTSv2.execute as execute
import JTSv2.process as process
import importlib.machinery
import multiprocessing
import configparser
import threading
import inspect
import queue
import time
import sys
import os


# TODO: Do logging
class ShellServer(threading.Thread):
    """
    The ShellServer is not the functional, but the structurial heart of the whole shell project, as it is the container
    for all main actors such as the command reference dictionary, the process list, the data nexus and the environmental
    variable container.
    The ShellServer Thread is supposed to be running during the whole runtime of the computer its running on. Starting
    through autostart and terminating with operating system shutdown. Whilst always running in the background, the
    ShellServer constantly observes the 'login' folder of the projects root directory, starting the requesting ui
    module as a subprocess and assigning it a freshly started Shell Thread, to actually execute issued commands.

    :ivar config_parser: (configparser.ConfigParser) The object containing the config specifications of the project,
    loaded from the config file of the project root

    :ivar project_directory: (string) The path of the project

    :ivar command_reference_dictionary: (CommandReferenceDictionary) The Dictionary containing the command references,
    specifically assigning the usable command names to the corresponding module names of the 'commands' folder

    :ivar process_list: (ProcessList) A Thread, managing the starting and garbage collection of running and terminated
    background commands or program connections

    :ivar shell_list: (list) a simple list object, keeping track of every started Shell instance

    :ivar env_variable_container: (EnvironmentalVariableContainer) The object containing the dictionary, assigning the
    contents of the environmental variables of the shell project env to their defined names

    :ivar data_nexus: (DataNexus) The platform, connecting processes together, by offering the option to provide data to
    the shell project environment and to request this data
    """
    def __init__(self):
        super(ShellServer, self).__init__()

        # updating the project path to the config file automatically, to prevent errors during later access on the
        # configured dependant pathsconfig_parser = configparser.ConfigParser()
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read("config.ini")
        # independently calculating the current path of the directory
        self.project_directory = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

        self.config_parser["Paths"]["project_dir"] = self.project_directory

        # setting up the command reference dictionary
        self.command_reference_dictionary = translate.CommandReferenceDictionary()
        self.command_reference_dictionary.add("test", "test")

        # setting up the process list
        self.process_list = process.ProcessList()
        self.process_list.start()

        # the list to keep track of all different shell instances
        self.shell_list = []

        # setting up the environmental variable container
        self.env_variable_container = datamanage.EnvironmentalVariableContainer()

        # lastly setting up the data Nexus and passing all the other management objects
        self.data_nexus = datamanage.DataNexus(self.process_list, self.env_variable_container,
                                               self.command_reference_dictionary)
        self.data_nexus.start()
        self.running = True

    def run(self):
        """
        The main loop of the 'ShellServer' Thread/ heart of the project runtime structure.
        Constantly observes the projects 'login' folder (empty on default). In case a file appears inside the folder, it
        was being created by a ui-program, that is attempting to connect to the JTShell system. The file is supposed to
        contain the full path of the python module, containing a 'main(in, out)' function, that will be started as a
        separate multiprocessing subprocess with queue connection to a also newly spawned 'Shell' Thread
        :returns: (void)
        """
        login_folder_path = ''.join([self.project_directory, "/login"])

        while self.running:

            # a little delay, as this loop, which si supposed to be running as long as the computer itself shouldn't
            # consume that much energy
            time.sleep(0.01)

            # putting the file paths of the files in the folder into one list
            file_list = []
            for name in os.listdir(login_folder_path):
                path = os.path.join(login_folder_path, name)
                if os.path.isfile(path):
                    file_list.append(path)

            if len(file_list) != 0:

                # iterating through the file list, reading the files content, which is supposed to be a singular string
                # of the requesting modules path, importing it dynamically and starting the main(inp, out) function of
                # the module as a subprocess with the input and output queues, connected to a newly spawned shell
                for file_path in file_list:
                    content_string = ""
                    with open(file_path, "r") as file:
                        content_string = file.readline()

                    if not(os.path.exists(content_string)):
                        # TODO: Display proper error message
                        break

                    # trying to run the main function of the module
                    try:
                        queue1 = multiprocessing.Queue()
                        queue2 = multiprocessing.Queue()

                        # Todo: design a shell list object
                        shell = Shell(self, queue2, queue1)
                        self.shell_list.append(shell)
                        module_process = multiprocessing.Process(target=_exec, args=(content_string, queue1,
                                                                                     queue2,))
                        # todo: create naming algorithm
                        self.process_list.append("interface1", module_process)
                        module_process.start()
                        shell.start()

                    except AttributeError:
                        # Todo: Display proper error message (popup)
                        pass

                    finally:
                        # removing the file, that was just used for login, so the server wont start infinitely many
                        # ui windows
                        os.remove(file_path)

    def stop(self):
        """
        This method stops the whole shell server system, including stopping every shell Thread, terminating every
        process and stopping the shell server itself.
        This ultimatly means every program, that is based on the shell server system is also stopped forcefully.
        This method should only be used for development or in emergencies
        Returns:
        void
        """
        # Stopping all the processes/ all the programs that were started with the shell server system
        self.process_list.stop_all()
        # Stopping the loops of all the shell threads
        for shell in self.shell_list:
            shell.running = False
        # Exiting python
        self.running = False
        exit(True)


def _exec(module_path, q1, q2):
    """
    Given the following problem:
    Attempting to use a imported function to execute as the target of a multiprocessing subprocess, an exception will
    be risen, because the imported function cannot be properly pickled (,which is necessary for the process start)

    This function poses a workaround to the problem, as the module is imported from within the subprocess by dynamic
    execution instead of the import getting in the way of process start.
    The function performs a absolute import of the target module, by using the 'module_path', then it calls the 'main'
    function of the module, passing it the two communication queues, as it is required for any program that is trying
    to perform a connection to a shell.
    :param module_path: (string) the full file path of the python module, that contains the program, which attempts to
    connect to a shell
    :param q1: (multiprocessing.Queue)
    :param q2: (multiprocessing.Queue)
    :return: (void)
    """
    exec_string_list = ["import importlib.machinery\n",
                        "module = importlib.machinery.SourceFileLoader('module.name','",
                        module_path.replace("\\", "/"),
                        "').load_module()\n",
                        "module.main(q1, q2)"]
    exec_string = ''.join(exec_string_list)
    compiled_string = compile(exec_string, r"<string>", "exec")
    exec(compiled_string)


# TODO: add command cache/ logging
class Shell(threading.Thread):
    """
    The Shell object is the Thread, that is started by the ShellServer main thread, whenever a program (mostly uis)
    requests the execution service of the shell project.
    The shells basically work by waiting for any issued commands/code to enter through the internal input queue,
    translating the python-ish console langunage into pure python expressions of equal effect, executing this code as
    a separate sub thread, fetching all messages issued by the executed program through the print queue and relaying
    those to the process, to which the shell has been initially connected, by putting the messages into the output
    queue.

    :ivar shell_server: (ShellServer) The reference to the ShellServer instance, that spawned the Shell

    :ivar input_queue: (multiprocessing.Queue) The queue, through which the code strings to be executed arrive

    :ivar output_queue: (multiprocessing.Queue) The queue, through which the infos, errors, results etc. of the executed
    commands are being sent back to the issueing program

    :ivar print_q: (multiprocessing.Queue) The queue, through which the print messages of the runnning code arrives
    """
    def __init__(self, shellserver, input_queue, output_queue):
        super(Shell, self).__init__()

        # keeping the reference to the server, so it can possibly be accessed later
        self.shell_server = shellserver

        # copying the fields of the server into own variables, as they can not only be considered as properties of the
        # top level management systematic, but also of the individual shells
        self.env_variable_container = self.shell_server.env_variable_container
        self.process_list = self.shell_server.process_list

        # The Queues from which the shell receives and sends its commands to the UIs inside the subprocesses
        self.input_q = input_queue
        self.output_q = output_queue

        # The running variable of the Thread
        self.running = True

        # The queue where print messages will be put in by the process
        self.print_q = multiprocessing.Queue()

        self.user_input_response = None

    def run(self):
        """
        the main loop of the 'Shell' Thread, first waiting for any code input to appear within the input queue, which is
        then being translated into proper standard python. The translated string will be used as the argument of the
        threaded execution process (utilizing the python interpreter).
        While the command is executed within a separate Thread it is supposed to be printing status information, error
        and result messages into the shell communication interface "ShellCom", which is ultimately linked to the shells
        'print_q' Queue. This print queue is then being observed as long as the Thread is alive. The messages arriving
        from the executed command in the printing queue are then redirected to the 'output_q' Queue of the shell, so
        that they can be displayed/processed by the connected user interface
        :return: (void)
        """
        while self.running:

            # waiting for the user input to be passed through the queue. The get() method of a Queue is blocking unless
            # that behaviour is specifically turned off
            user_input = self.input_q.get()

            # translating the user input with the translate function, essentially converting the shell syntax elements
            # into standard python syntax, so it can be executed by the interpreter
            translated_string = translate.translate(user_input, self.shell_server.command_reference_dictionary)

            # executing the user input as a Thread, because the main loop of this Shell-Thread has to be waiting for the
            # print messages to come in, as the command is being executed
            try:
                foreground_thread = threading.Thread(target=execute.execute, args=(self, translated_string,))
                foreground_thread.start()

                while foreground_thread.is_alive():
                    # not to overload the processor, can be tweeked at higher loads
                    time.sleep(1/1000)
                    # fetching the output from the command and putting it into the output queue to the ui
                    # the try statement is important to catch the queue.Empty exception of the non blocking queue
                    # get access, which in turn is needed for proper function of the loop, as a blocking call would hang
                    # the program at least at every second background function
                    try:
                        execute_output = self.print_q.get(block=False)
                        # checking whether an input prompt has been issued by the executed shell, by delivering an
                        # InputPromptMessage
                        self.output_q.put(execute_output)
                        # checking whether an input prompt has been issued by the executed shell, by delivering an
                        # InputPromptMessage
                        if isinstance(execute_output, datamanage.InputPromptMessage):
                            while True:
                                try:
                                    self.user_input_response = self.input_q.get()
                                    break
                                except queue.Empty:
                                    pass
                    except queue.Empty:
                        pass

                time.sleep(0.01)
                # printing the messages, that migh have gotten stuck in the queue just after Thread termination
                while not(self.print_q.empty()):
                    try:
                        execute_output = self.print_q.get(block=False)
                        self.output_q.put(execute_output)
                    except queue.Empty:
                        pass

            # printing a possible exception to the ui
            except Exception as e:
                self.output_q.put(datamanage.ErrorMessage(e))

    def get_input(self):
        while self.user_input_response is None:
            time.sleep(1/1000)
        temp = self.user_input_response
        self.user_input_response = None
        return temp