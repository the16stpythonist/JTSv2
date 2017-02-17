__author__ = 'Jonas'
import multiprocessing
import configparser
import threading
import pickle
import sys
import os

# THE FUNCTIONS WHICH ARE USED AS THE CONDITIONS FOR THE SUB DICT CREATION OF THE ENV. VARIABLE CONTAINER#


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

    def keys(self):
        """
        The keys method of a dictionary style container object
        Returns:
        The list of keys of the internal dictionary
        """
        return self.dict.keys()

    def complying_items(self, function):
        """
        Creates a sub dictionary of the main variable dictionary for every key, value pair, that complies the condition
        posed by the 'function'  passed, which means the sub dictionary will hold only those key, value pairs, which
        if passed as parameters to 'function' produced a 'True' return.
        Args:
            function: The boolean function, with two positional parameters, the first one resembling the key and the
                second one the value of a dictionary item. Hast to return a boolean.

        Returns:
        The sub dictionary for all the items that matched the posed comply the posed condition
        """
        # Looping through the whole dictionary and adding every key value pair to the sub dict, for which the
        # specified 'function' returns True
        sub_dict = {}
        for key, value in self.dict.items():
            if function(key, value):
                sub_dict[key] = value
        return sub_dict

    def variables_starting_with(self, substring):
        """
        Creates a sub dictionary for all the items, whose key starts with the substring 'substring'
        Args:
            substring: The substring the variables have to start with

        Returns:
        The dict with all items, which means env. variables, whose keys start with the substring
        """
        return self.complying_items(lambda key, value: self.key_starts_with(key, substring))

    def variables_containing_substring(self, substring):
        """
        Creates a sub dictionary for all the items, whose key contain the substring 'substring'
        Args:
            substring: The string, the variable names have to contain

        Returns:
        The dict with all items, which means env. variables, whose keys contain the substring
        """
        return self.complying_items(lambda key, value: self.substring_in_key(key, substring))

    def variables_having_type(self, class_or_type):
        """
        Creates a sub dictionary for all the variables, whose values have the specified type
        Args:
            class_or_type: The CLASS or type specification to check for

        Returns:
        Tge dict, with all items, which means env. variables, whose values have the specified type
        """
        return self.complying_items(lambda key, value: self.value_is_type(value, class_or_type))

    def save(self, key):
        """
        Saves the temporary contents of the variable as stored in the internal dictionary into their according file
        Args:
            key: The string name of the variable to save

        Returns:
        void
        """
        if key in self.dict.keys():
            variable_path = "{}\\{}".format(self.variable_directory, key)
            # Saving the pickled data into the files
            with open(variable_path, mode="wb") as file:
                pickle.dump(self[key], file)

    def save_all(self):
        """
        Saves all the variables as pickled data into individual files inside a folder of the porject
        Returns:
        void
        """
        # For every variable name of the variables stored in the internal dictionary
        for key in self.keys():
            self.save(key)

    def __setitem__(self, key, value):
        """
        This is the magic method for assigning a new dictionary item by the statement:
        object[key] = value
        If such a assignment is performed with a env. variable container, the according value is changed in case the
        specified env. variable already existed, in case its supposed to be a new variable the file in the env.
        variable folder is created as well.
        Args:
            key: The key of the dictionary entry to be modified/ added
            value: The new value for the given key

        Returns:
        void
        """
        # First checks whether a variable with the specified name already exists, in case it dies not, creates a new
        # file in the folder, where the env. variables are stored and writes the pickled data into the file
        if key not in self.dict.keys():
            variable_path = "{}\\{}".format(self.variable_directory, key)
            # The windows system command for creating a new file
            os.system("copy NUL {}".format(variable_path))
            with open(variable_path, mode="wb") as file:
                pickle.dump(value, file)
        # In any case, whether the variable already exists or not takes up the Key value pair into the internal dict
        self.dict[key] = value

    def __getitem__(self, key):
        """
        This is the magic method for when a object is indexed. The value inside the index brackets will be passed to
        this method as the 'key' parameter.
        Args:
            key: The key for the item one wants

        Returns:
        The value of the item specified by 'key'
        """
        return self.dict[key]

    def __delitem__(self, key):
        """
        This is the magic method for when a item of the container is supposed to be deleted by the 'del' operator
        del object[key]
        Args:
            key: -

        Returns:
        void
        """
        if key in self.dict.keys():
            del self.dict[key]
            variable_path = "{}\\{}".format(self.variable_directory, key)
            os.remove(variable_path)
        else:
            raise KeyError("There is no variable by the name {}".format(str(key)))

    @staticmethod
    def key_starts_with(key, substring):
        """
        Whether or not the string given as 'key' starts with the sub string given as 'substring'
        Notes:
            This method is mainly used to classify the items of the env. variable dictionary for whether or not they
            should be added to a specific sub dict.
        Args:
            key: The string key to be checked
            substring: The substring to check for

        Returns:
        The boolean value of whether or not the key starts with the specified substring
        """
        return key[0:len(substring)] == substring

    @staticmethod
    def substring_in_key(key, substring):
        """
        Whether or not the string given by 'substring' is a sub string of the string 'key'
        Notes:
            This method is mainly used to classify the items of the env. variable dictionary for whether or not they
            should be added to a specific sub dict.
        Args:
            key: The string key to be checked for potentially having the substring
            substring: The substring to check for

        Returns:
        The boolean value of whether or not the substring is in the key string
        """
        return substring in key

    @staticmethod
    def value_is_type(value, class_or_type):
        """
        Whether or not the object value is of the type specified by 'class_or_type'
        Args:
            value: The value to check the type of
            class_or_type: The type, the value is supposed to have

        Returns:
        Whether or not the value has the specified type
        """
        return isinstance(value, class_or_type)

    @staticmethod
    def value_is_same_type(value, obj):
        """
        Whether or not the object 'value' is the same type as the object 'obj'
        Args:
            value: The first object for the type comparison
            obj: The second object for the type comparison

        Returns:
        Whether or not the object 'value' is the same type as the object 'obj'
        """
        return type(value) == type(obj)


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
    The ShellCom base class for the process to shell communication. An instance of such an object HAS to be passed to
    every command-function, however, this does not have to be done by the user, but an instance of this is automatically
    being passed to every command function as its first positional parameter.
    ShellCom objects are generally used as the access to the environmental variables of the Shell system. The method
    of accessing the variables however is very inefficient as for each call all environmental variables are read from
    the file system and then stored in an internal dict. The class implements the magic methods for dictionary
    behaviour, which means that variables can be accessed by simply indexing the ShellCom object with their string name.
    Attributes:
        env_variables: The dictionary storing all the temp
    """
    def __init__(self, shell_server):
        self.shell_server = shell_server
        # Storing the project directory from the shell server in its own variable
        self.project_path = self.shell_server.project_directory
        # Storing the important shell level Threads as their individual variables.
        self.env_variable_container = self.shell_server.env_variable_container
        self.process_list = self.shell_server.process_list
        self.command_reference_dict = self.shell_server.command_reference_dictionary

    def print_info(self, string):
        self._print(InfoMessage(string))

    def print_error(self, exception):
        self._print(ErrorMessage(exception))

    def print_result(self, string):
        self._print(ResultMessage(string))

    def complying_variables(self, function):
        """
        Creates a sub dictionary of the main variable dictionary for every key, value pair, that complies the condition
        posed by the 'function'  passed, which means the sub dictionary will hold only those key, value pairs, which
        if passed as parameters to 'function' produced a 'True' return.
        Args:
            function: The boolean function, with two positional parameters, the first one resembling the key and the
                second one the value of a dictionary item. Hast to return a boolean.

        Returns:
        The sub dictionary for all the items that matched the posed comply the posed condition
        """
        return self.env_variable_container.complying_items(function)

    def variables_starting_with(self, substring):
        """
        Creates a sub dictionary for all the items, whose key starts with the substring 'substring'
        Args:
            substring: The substring the variables have to start with

        Returns:
        The dict with all items, which means env. variables, whose keys start with the substring
        """
        return self.env_variable_container.variables_starting_with(substring)

    def variables_containing_substring(self, substring):
        """
        Creates a sub dictionary for all the items, whose key contain the substring 'substring'
        Args:
            substring: The string, the variable names have to contain

        Returns:
        The dict with all items, which means env. variables, whose keys contain the substring
        """
        return self.env_variable_container.variables_containing_substring(substring)

    def variables_having_type(self, class_or_type):
        """
        Creates a sub dictionary for all the variables, whose values have the specified type
        Args:
            class_or_type: The CLASS or type specification to check for

        Returns:
        Tge dict, with all items, which means env. variables, whose values have the specified type
        """
        return self.env_variable_container.variables_having_type(class_or_type)

    def stop_all(self):
        """
        Stops the whole shell server system, which also means terminating every program associated with it.
        Returns:
        void
        """
        self.env_variable_container.save_all()
        self.shell_server.stop()

    def variable_kivy_info(self, key):
        """
        The kivy string format for the information about the variable, specified by its string name 'key'.
        The information contains the name, the type, the size, and the actual content of the variable
        Args:
            key: The name of the variable for which the information is supposed to be gathered

        Returns:
        The string, that displays the information about the specified variable (in kivy format)
        """
        if key in self.env_variable_container.keys():
            value = self[key]
            string_list = list(["VARIABLE INFORMATION"])
            string_list.append("\nname: [color=3AD126]{}[/color]\n".format(key))
            string_list.append("type: {}\n".format(str(type(value))))
            string_list.append("size: {} Byte\n".format(sys.getsizeof(value)))
            string_list.append("content:\n{}\n".format(str(value)))
            return ''.join(string_list)
        else:
            raise KeyError("There is no variable of the name {}".format(key))

    def keys(self):
        """
        The keys method of a dictionary style container object
        Returns:
        The list of variable names
        """
        return self.env_variable_container.dict.keys()

    def __getitem__(self, key):
        """
        This is the magic method for when a object is indexed. The value inside the index brackets will be passed to
        this method as the 'key' parameter.
        The ShellCom objects act as dictionary like containers for the envirnomental variables of the shell system and
        in case they are indexed with the string name of such a env. variable the value of this variable is returned in
        response
        Args:
            key: The string name of the env. variable, whose value is to be returned

        Returns:
        The value of the variable addressed
        """
        # First checking if there actually is a variable by this name in the container
        if key in self.env_variable_container.keys():
            return self.env_variable_container[key]
        else:
            error_string = "There is no environmental variable by the name {}".format(str(key))
            raise AttributeError(error_string)

    def __setitem__(self, key, value):
        """
        This is the magic method for assigning a new dictionary item by the statement:
        object[key] = value
        If such an assignment is being used with a ShellCom object, the specified env. variable with the name "key" is
        either created or modified
        Args:
            key: The string name of the variable, that is supposed to be created / modified
            value: The new value for the specified variable

        Returns:
        void
        """
        self.env_variable_container[key] = value

    def _print(self, msg):
        pass

    @staticmethod
    def get_variables_plain_string(variable_dict, whitespace=1, show_size=False):
        string_list = ["\n"]
        for key, value in variable_dict.items():
            string_list.append(key)
            spaces = " " * whitespace
            string_list.append("{}-{}".format(spaces, spaces))
            string_list.append(str(type(value)))
            if show_size:
                string_list.append("{}-{}".format(spaces, spaces))
                string_list.append("{} B".format(sys.getsizeof(value)))
            string_list.append("\n")
        return ''.join(string_list)

    @staticmethod
    def get_variables_kivy_string(variable_dict, column_width=45, show_size=True):
        string_list = ["\n"]
        for key in sorted(variable_dict.keys()):
            value = variable_dict[key]
            string_list.append("[color=3AD126]{}[/color]{}".format(key, " " * (column_width - len(key))))
            value_type = str(type(value))
            string_list.append("{}{}".format(value_type, " " * (column_width - len(value_type))))
            if show_size:
                size = "{} B".format(str(sys.getsizeof(value)))
                string_list.append("{}{}".format(size, " " * (column_width - len(size))))
            string_list.append("\n")
        return ''.join(string_list)


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