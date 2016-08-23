__author__ = 'Jonas'
import multiprocessing
import configparser
import threading
import pickle
import os


class EnvironmentalVariableContainer:
    """
    The object, that holds the environmental variables during runtime within an internal dictionary. Environmental
    variables have to be assigned with the prefix of a dollar character '$', in the same way they can also be accessed
    by simply utilizing their name as part of the shells python-ish execution language, as the variable names are
    being translated to be the string keys for a dictionary access of this object

    After the runtime of the program the current content/state of the environmental variables are being saved into
    separate files, named as the variables, containing the pickled byte code representation of those variables, which
    are being loaded into the dictionary on program/computer start again.
    Therefore it is important, that objects, that are being stored in the Container have to be explicitly pickelable.

    :ivar config: (configparser.ConfigParser) The object, holding the information of the projects config file, that also
    includes the path to the folder, containing the pickled variables

    :ivar variable_directory: (string) the path of the folder, containing the pickled variables

    :ivar dict: (dictionary) The dictionary holding the variables names as keys to their corresponding values
    """
    def __init__(self):
        # reading the path of the directory, in which the pickled variables are stored from the config file, by using
        # pythons 'configparser' module
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.variable_directory = self.config["Paths"]["variables_dir"]

        self.dict = {}
        # itering through the files of the specified directory and attempting to unpickle them into the dictionary
        self.load()

    def load(self):
        """
        loads the variables, that are stored as separate pickled files in the configured directory (on default the
        'env_vars' folder of the project) unpickled into the dictionary of the EnvironmentalVariableContainer object,
        using the former file name as new variable name/key
        :return:
        """
        # itering through the variable directory with the os.walk function and attempting to unpickle the variables
        for subdir, dirs, files in os.walk(self.variable_directory):
            for filename in files:
                file_path = os.path.abspath(os.path.join(subdir, filename))
                with open(file_path, "rb") as file:
                    self.dict[filename] = pickle.load(file)

    def __setitem__(self, key, value):
        if key not in self.dict.keys():
            variable_path = "{}\\{}".format(self.variable_directory, key)
            os.system("copy NUL {}".format(variable_path))
            with open(variable_path, mode="wb") as file:
                pickle.dump(value, file)
        self.dict[key] = value

    def __getitem__(self, item):
        return self.dict[item]


# TODO: add the shell list to the DataNexus's services
# TODO: add a method, that returns help for all provider possibilities
# TODO: Implement the providers
class DataNexus(threading.Thread):
    """
    One of the more advanced features of the whole shell project being the DataNexus object, which is aspired to provide
    a cross process platform of accessing internal shell system informations, as well as multiple other methods
    provided by third party processes/programs connected to the DataNexus.

    The DataNexus works by

    :ivar process_list: (ProcessList) A reference to the ProcessList of the shell server

    :ivar
    """
    def __init__(self, process_list, environmental_variables, command_reference):
        # initializing the super class
        super(DataNexus, self).__init__()

        # the requesters dictionary is going to keep track of the processes, that registered to be eventually using the
        # nexus service to redirect data offered by the 'providers'. The dictionary uses the process names as keys to
        # the the queues connected to those processes, because later on the incoming requests will contain the name of
        # the requesting process to respond to
        self.requesters = {}
        # the providers dictionary keeps track of those processes, that offer their functionalities/variables to be
        # available to every other client of the nexus
        self.providers = {}

        # creating references to the first level providers, the shell servers main management units
        self.process_list = process_list
        self.env_variables = environmental_variables
        self.cmd_ref = command_reference
        # those are the names of the shell providers, as they have to be used by any requesting instance.
        # Note how the nexus itself also provides informational service
        self.shell_providers = ["process_list", "env_vars", "cmd_ref", "data_nexus"]

        self.requests = multiprocessing.Queue()

    def run(self):

        while True:

            # waiting for requests to enter the request queue
            request = self.requests.get()

            # the request, consisting of 'DataRequest' objects, which in turn contain the name of the requesting
            # process, the name of the provider of the data and the specific content
            if isinstance(request, DataRequest):

                requested_provider = request.requested_provider_name
                if requested_provider in self.shell_providers:
                    try:
                        function_return = getattr(getattr(self, requested_provider),
                                                  request.requested_function_call)(*request.function_arguments,
                                                                                   **request.function_keyword_arguments)

                        self.requesters[request.requesting_process_name].put(function_return)

                    # TODO: Think of how you can use those exceptions
                    except AttributeError:
                        pass

                    except KeyError:
                        pass

                    except pickle.PickleError:
                        pass


class DataRequest:

    def __init__(self, processname, providername, requestfunction, args, kwargs):
        self.requesting_process_name = processname
        self.requested_provider_name = providername
        self.requested_function_call = requestfunction
        self.function_arguments = args
        self.function_keyword_arguments = kwargs


class ShellCom:
    """
    The ShellCom base class for the process to shell communication, that HAS to be passed to every command(-module) that
    is being executed, since it not only provides the access point to the DataNexus and therefore information about the
    entirety of the shell environment to the process, but also provides the necessary queue connections for the process/
    command to first relay data to the Shell Thread, that is later on printed as Messages on a ui.
    """
    def __init__(self, data_nexus):
        self.request_queue = data_nexus.requests
        self.env_variables = {}
        config_parser = configparser.ConfigParser()
        config_parser.read("config.ini")
        self.project_path = config_parser["Paths"]["project_dir"]

    def print_info(self, string):
        self._print(InfoMessage(string))

    def print_error(self, exception):
        self._print(ErrorMessage(exception))

    def print_result(self, string):
        self._print(ResultMessage(string))

    def __getitem__(self, key):
        self._update_env_variables()
        return self.env_variables[key]

    def __setitem__(self, key, value):
        self._update_env_variables()
        if key not in self.env_variables.keys():
            variable_path = "{}\\{}\\{}".format(self.project_path, "env_vars", key)
            os.system("copy NUL {}".format(variable_path))
            with open(variable_path, mode="wb") as file:
                pickle.dump(value, file)
        self.env_variables[key] = value

    def _print(self, msg):
        pass

    def _update_env_variables(self):
        """
        updates the environmental variables inside the 'env_vars' folder into the local dictionary of the object
        :return: (void)
        """
        for key in os.listdir("{}\\env_vars".format(self.project_path)):
            filepath = ''.join([self.project_path, "\\env_vars\\", key])
            with open(filepath, mode="rb") as file:
                self.env_variables[key] = pickle.load(file)


# Todo: extend Shellcom utility
class ForegroundShellCom(ShellCom):

    def __init__(self, data_nexus, shell):
        super(ForegroundShellCom, self).__init__(data_nexus)
        self.shell = shell

    def print_info(self, string):
        self._print(InfoMessage(string))

    def print_error(self, exception):
        self._print(ErrorMessage(exception))

    def print_result(self, string):
        self._print(ResultMessage(string))

    def prompt_input(self, prompt):
        self._print(InputPromptMessage(prompt))
        return self.shell.get_input()

    def _print(self, msg):
        self.shell.print_q.put(msg)


class BackgroundShellCom(ShellCom):

    def __init__(self, data_nexus, process_output_queue):
        super(BackgroundShellCom, self).__init__(data_nexus)
        self.output_queue = process_output_queue

    def print_error(self, exception):
        self.output_queue.put(ErrorMessage(exception))

    def print_result(self, string):
        self.output_queue.put(ResultMessage(string))


class Message:

    message_color_dict = {"white": "DEDEDE",
                          "red": "D61818",
                          "green": "3AD126",
                          "blue": "397AD4",
                          "magenta": "D439B7"}

    def __init__(self, string, prefix, short_prefix, color):
        """
        an object representing a message or outcome information of a command, mainly to encapsulate the information
        of such a message's content, type, ui coloring and prefix info in a single object, that can be transported through a
        multiprocessing Queue and also easily accessed

        :ivar content: (string) The content of the message

        :ivar prefix: (string) The prefix of the message, indicating the user in a non color ui, which type of message is
        being displayed (error, info, result...) in square brackets
        EXAMPLE:
        [PREFIX] content...

        :ivar short_prefix: (string) The short symbol for the message type, being an alternative prefix to a full word
        EXAMPLE:
        [i] content...

        :ivar color: (string) the name of a color (that has to exist in the internal color dictionary), in which the message
        should appear, if possible in the corresponding ui environment
        """
        self.content = string

        # adding the brackets to the prefix strings
        self.prefix = self._add_prefix_brackets(prefix)
        self.short_prefix = self._add_prefix_brackets(short_prefix)

        # color
        self.color_name = ""
        self.color = ""
        if color in self.message_color_dict.keys():
            self.color_name = color
            self.color = self.message_color_dict[self.color_name]

        elif color[0] == "#" and len(color) == 7:
            self.color = color

        else:
            self.color_name = "white"
            self.color = self.message_color_dict[self.color_name]

    def get_string(self, short_prefix=False):
        """
        Returns the string representation of the Message
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :return: (string)
        """
        pass

    def __str__(self):
        return self.get_string()

    @staticmethod
    def _add_prefix_brackets(prefix_string):
        """
        puts the string into the '[]' brackets, so it is marked as a message type prefix, signaling which type of
        message is being displayed.
        :param prefix_string: the prefix, which to put into the brackets
        :return: (string) the prefix string within the brackets
        """
        return ''.join(["[", prefix_string, "]"])


class InfoMessage(Message):
    """
    an object representing a informational message about a runtime event of the corresponding command, mainly to
    encapsulate the information of such a message's content, type, ui coloring and prefix info in a single object, that
    can be transported through a multiprocessing Queue and also easily accessed

    :ivar content: (string) The content of the message

    :ivar prefix: (string) The prefix of the message, indicating the user in a non color ui, which type of message is
    being displayed (error, info, result...) in square brackets
    EXAMPLE:
    [PREFIX] content...

    :ivar short_prefix: (string) The short symbol for the message type, being an alternative prefix to a full word
    EXAMPLE:
    [i] content...

    :ivar color: (string) the name of a color (that has to exist in the internal color dictionary), in which the message
    should appear, if possible in the corresponding ui environment
    """

    def __init__(self, string):
        super(InfoMessage, self).__init__(string, "INFO", "*", "white")

    def get_string(self, short_prefix=False):
        """
        Returns the string representation of the Message
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :return: (string)
        """
        return_string_list = []
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append(" ")
        return_string_list.append(self.content)
        return ''.join(return_string_list)

    def get_kivy(self, short_prefix=False):
        """
        Returns the string representation of the string, in addition to the color information of the Message added in
        form of the kivy markup language tags, to be compatible to print onto a kivy label/widget.
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :param newline: (boolean) whether a new line should be started after displaying the prefix or not
        :return: (string)
        """
        return_string_list = ["[color={0}]".format(self.color), "[b]"]
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append("[/b]")
        return_string_list.append(" ")
        return_string_list.append(self.content)
        return_string_list.append("[/color]")
        return ''.join(return_string_list)


# TODO: Maybe add Traceback information and origin process information
class ErrorMessage(Message):
    """
    an object representing a message about a exception occuring in the corresponding command, mainly to encapsulate
    of such a message's content, type, ui coloring and prefix info in a single object, that can be transported through a
    multiprocessing Queue and also easily accessed

    :ivar content: (string) The content of the message

    :ivar prefix: (string) The prefix of the message, indicating the user in a non color ui, which type of message is
    being displayed (error, info, result...) in square brackets
    EXAMPLE:
    [PREFIX] content...

    :ivar short_prefix: (string) The short symbol for the message type, being an alternative prefix to a full word
    EXAMPLE:
    [i] content...

    :ivar color: (string) the name of a color (that has to exist in the internal color dictionary), in which the message
    should appear, if possible in the corresponding ui environment

    :ivar exception_name: (string) The Type of exception passed as content of the error
    """
    def __init__(self, excepetion):
        # setting the exceptions content as the main message string
        string = str(excepetion)
        super(ErrorMessage, self).__init__(string, "ERROR", "!", "red")

        # adding a field for the exceptions name
        self.exception_name = type(excepetion).__name__

    def get_string(self, short_prefix=False):
        """
        Returns the string representation of the Error/Exception in the following form:

        [PREFIX] ExcpetionName
        error message of the exception

        :param short_prefix: whether the shortened prefix is to be used or not
        :return: (string)
        """
        return_string_list = []
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append(" ")
        return_string_list.append(self.exception_name)
        return_string_list.append("\n")
        return_string_list.append(self.content)
        return ''.join(return_string_list)

    def get_kivy(self, short_prefix=False):
        """
        Returns the string representation of the string, in addition to the color information of the Message added in
        form of the kivy markup language tags, to be compatible to print onto a kivy label/widget.
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :param newline: (boolean) whether a new line should be started after displaying the prefix or not
        :return: (string)
        """
        return_string_list = ["[color={0}]".format(self.color), "[b]"]
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append("[/b] {0}\n".format(self.exception_name))
        return_string_list.append("{0}[/color]".format(self.content))
        return ''.join(return_string_list)


class ResultMessage(Message):
    """
    an object representing a result message or outcome information of a command, mainly to encapsulate the information
    of such a message's content, type, ui coloring and prefix info in a single object, that can be transported through a
    multiprocessing Queue and also easily accessed

    :ivar content: (string) The content of the message

    :ivar prefix: (string) The prefix of the message, indicating the user in a non color ui, which type of message is
    being displayed (error, info, result...) in square brackets
    EXAMPLE:
    [PREFIX] content...

    :ivar short_prefix: (string) The short symbol for the message type, being an alternative prefix to a full word
    EXAMPLE:
    [i] content...

    :ivar color: (string) the name of a color (that has to exist in the internal color dictionary), in which the message
    should appear, if possible in the corresponding ui environment
    """
    def __init__(self, string):
        super(ResultMessage, self).__init__(string, "RESULT", "+", "green")

    def get_string(self, short_prefix=False, newline=False):
        """
        Returns the string representation of the Message
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :param newline: (boolean) whether a new line should be started after displaying the prefix or not
        :return: (string)
        """
        return_string_list = []
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append(" ")
        if newline:
            return_string_list.append("\n")
        return_string_list.append(self.content)
        return ''.join(return_string_list)

    def get_kivy(self, short_prefix=False, newline=False):
        """
        Returns the string representation of the string, in addition to the color information of the Message added in
        form of the kivy markup language tags, to be compatible to print onto a kivy label/widget.
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :param newline: (boolean) whether a new line should be started after displaying the prefix or not
        :return: (string)
        """
        return_string_list = ["[color={0}]".format(self.color), "[b]"]
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append("[/b] ")
        if newline:
            return_string_list.append("\n")
        return_string_list.append("{0}[/color]".format(self.content))
        return ''.join(return_string_list)


class InputPromptMessage(Message):

    def __init__(self, string):
        super(InputPromptMessage, self).__init__(string, "INPUT", "IN", "blue")

    def get_string(self, short_prefix=False, newline=False):
        """
        Returns the string representation of the Message
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :param newline: (boolean) whether a new line should be started after displaying the prefix or not
        :return: (string)
        """
        return_string_list = []
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append(" ")
        if newline:
            return_string_list.append("\n")
        return_string_list.append(self.content)
        return ''.join(return_string_list)

    def get_kivy(self, short_prefix=False, newline=False):
        """
        Returns the string representation of the string, in addition to the color information of the Message added in
        form of the kivy markup language tags, to be compatible to print onto a kivy label/widget.
        :param short_prefix: (boolean) whether the shortened prefix is to be used or not
        :param newline: (boolean) whether a new line should be started after displaying the prefix or not
        :return: (string)
        """
        return_string_list = ["[color={0}]".format(self.color), "[b]"]
        if short_prefix:
            return_string_list.append(self.short_prefix)
        else:
            return_string_list.append(self.prefix)
        return_string_list.append("[/b] ")
        if newline:
            return_string_list.append("\n")
        return_string_list.append("{0}[/color]".format(self.content))
        return ''.join(return_string_list)