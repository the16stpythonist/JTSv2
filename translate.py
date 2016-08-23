__author__ = 'Jonas'
import re
import os
import pickle
import inspect
import configparser
import JTSv2.execute as execute
import JTSv2.lib.stringutil as stringops


ILLEGAL_CHARACTERS_FUNCTION_NOMENCLATURE = [" ", ",", ".", "-", "+"]


def translate(input_str, commandreferencedictionary):
    translated_string = _translate_environmental_variables(input_str)
    translated_string = _translate_commands(translated_string, commandreferencedictionary)
    return translated_string


def _translate_environmental_variables(input_string):
    """
    given the string of the terminal input this function will translate referenced environmental variables (Env
    variables are specified by adding a dollar '$' prefix to the variable name, example '$test = 3') into strings, that
    are used as keys for the 'EnV' Dictionary, example 'EnV['$test'] = 3', as that is the EnvironmentalVariableContainer
    as he is known within the execute methods namespace.

    EXAMPLE:
    "$Hallo = $No and '$Hallo'"
    > "EnV['$Hallo'] = EnV['$No'] and '$Hallo'"

    :param input_string:
    :return:
    """
    translated_string = input_string
    env_variable_list = _find_environmental_variables(input_string)
    for variable_name in env_variable_list:
        translated_string = stringops.replace_ignore_in_quotationmarks(translated_string, variable_name,
                                                                       "EnV['{}']".format(variable_name.replace('$',
                                                                                                                '')))
    return translated_string


def _translate_commands(input_string, commandreferencedictionary):
    """
    given the string of the terminal input, this function will essentially use the CommandReferenceDictionary of the
    main shell environment to translate the commands used in the terminal into function calls, that the python
    Interpreter can process. Because of how the program works a command call relates to a separated module within the
    'commands' subpackage, the translation therefore adds additional lines to the input string, dynamically importing
    the modules, that were referenced by the used commands. The actual functionality of such a command is executed
    by a 'main' function of the corresponding module (A main function MUST always exist).
    Additionally the function also translates the exclamation mark '!' and question mark '?' Syntax:

    The exclamation mark implies a background execution of the prefixed command, being translated into
    'self.background('module.main(params...)')', utilizing the background function within the execute module to open
    a background process. The passed self argument is the Executer object (inside which the translated string will
    actually compiled and ran), that is the central instance within the new process.

    The question mark implies the call of a help function for the prefixed command, being translated into
    'help('modulename')', utilizing the help function within the execute module to ultimatly access the help dictionary
    of the module (It is not necessary, but strongly recommended)

    EXAMPLE:
    "cmd2('hello') and !cmd1('not') and ?cmd1()"
    > "import JTSv2.commands.mod1 as mod1
       import JTSv2.commands.mod2 as mod2
       mod2.main(self.shell,'hello')) and self.background('''mod1.main(self.shell,'nothing)')''') and help('''mod1''')"

    :param input_string:
    :param commandreferencedictionary:
    :return:
    """
    translated_string = input_string
    necessary_imports_list = []

    command_list = _find_whole_commands(input_string)

    for command in command_list:
        command_name = _get_commandname(command).replace("!", "").replace("?", "")

        # checking whether the current function call is a legit custom command or a python builtin, that is being used
        # in case the reference dictionary doesnt know the command name, assuming it is a builtin or whatever
        # skipping to the next command
        if not(commandreferencedictionary.is_command(command_name)):
            continue

        # creating the string of the import statement of the execute command, as the actual functions are within
        # separate modules, they are dynamically imported, only within a temporary executional namespace
        import_string = "import JTSv2.commands."
        module_name = commandreferencedictionary.get_modulename(command_name)
        # the newline after the statement is important
        import_string = ''.join([import_string, module_name, " as ", module_name, "\n"])
        necessary_imports_list.append(import_string)

        # In case there is a exclamation mark in front of the command, this means, that the command si supposed to be
        # run as a background process, therefore putting the main function call into background() function call, which
        # is a function within the execute module, that expects an executer object and the execution statement as string
        # so it can execute it as a Process.
        translated_command = ""
        if command[0] == "!":
            translated_command = ''.join(["background(shell, ('''",
                                          "import JTSv2.commands.", command_name, " as ", command_name, "\n",
                                          stringops.replace_ignore_in_quotationmarks(command, "!" + command_name + "(",
                                                                                     module_name+".main(bg_com,"),
                                          "'''))"])

        elif command[0] == "?":
            translated_command = ''.join(["help('''", module_name, "''')"])

        else:
            translated_command = stringops.replace_ignore_in_quotationmarks(command, command_name + "("
                                                                            , module_name+".main(fg_com,")

        translated_string = stringops.replace_ignore_in_quotationmarks(translated_string, command, translated_command)

    # getting rid of double imports, caused by the same command being called multiple times
    necessary_imports_list = list(set(necessary_imports_list))
    necessary_imports_list.sort()
    imports_string = ''.join(necessary_imports_list)

    translated_string = ''.join([imports_string, translated_string])

    return translated_string


def _find_command_names(input_str):
    """
    If given the string of a terminal input, the function will  search for all command calls within the input and then
    return a list containing the names of all commands that are called.
    The Commands are identified by the brackets they have to be followed by just as they have to in regular python

    EXAMPLE:
    "Command() and Test()"
    > ['Command', 'Test']

    :param input_str: (string) the terminal input issued by the user
    :returns: (list)
    """
    command_list = []
    reg = re.compile("""[^().,\-+"'#*'\s]*\(""")
    for string in stringops.split_string_structures(input_str):
        if not((string[0] == "'" or string[0] == '"') and (string[-1] == "'" or string[-1] == '"')):
            command_list += re.findall(reg, string)
    return list(map(lambda x: x.replace(" ", "").replace("(", ""), command_list))


def _get_commandname(command_string):
    """
    if given the string of a whole command, returns only the name of the command

    EXAMPLE:
    'Command(100, 'hello')'
    > 'Command'

    :param command_string:
    :return:
    """
    return command_string[:command_string.find("(")]


def _find_whole_commands(input_str):
    """
    If given a string, that once came from a terminal input, this function will find every function call within the
    string. The whole function, with brackets and parameters included will then be added to a command list, which will
    also be returned.
    The function will also separately append every nested function (functions, that were passed as parameters) at any
    given recursive depth.

    EXAMPLE:
    "This(This('hallo')) and That('not()')"
    > ["This(This('hallo'))", "That('not()')", "This('hallo')"]

    :param input_str: (string) the string, that is supposed to contain function calls, that have to get found
    :return: (list) a list of string, that contain the whole function calls with the bracket body
    """
    command_list = []
    string_list = stringops.split_string_structures(input_str)

    # the algorithm will go through the string list, that was separated by the "split_string_structures" function of
    # the stringops module, that returns the string contents split by whether they are enclosed by quotes or not.
    # Inside the strings, that are not 'quoted', it'll first search commands with the
    # '_find_commands_without_string_parameters(string)' function and append those to the command list.
    # Furthermore the actual procedure will count the excess opening brackets of string before the quoted string, to
    # determine how many pairs of brackets enclose the quoted part. By itering through the string in reverse the
    # functionparts to the according excess brackets are added to a temporary string. In case there are excess opening
    # brackets, evrything is added to the temporary list until there are enough (not already paired) closing brackets
    # in a further substring, so that the temp string can be added as new command

    incomplete_command = []
    excess_opening_brackets = 0
    for string in string_list:
        if not((string[0] == "'" or string[0] == '"') and (string[-1] == "'" or string[-1] == '"')):
            command_list += _find_commands_without_string_parameters(string)

            carryover = excess_opening_brackets
            if excess_opening_brackets > 0:
                bracket_balance = 0
                temporary_character_list = []
                for character in string:
                    temporary_character_list.append(character)
                    if character == "(":
                        bracket_balance -= 1
                    elif character == ")":
                        bracket_balance += 1
                        if bracket_balance == excess_opening_brackets:
                            incomplete_command.append(''.join(temporary_character_list))
                            command_list.append(''.join(incomplete_command))
                            incomplete_command = []
                            break

                incomplete_command.append(''.join(temporary_character_list))

            excess_opening_brackets = string.count("(") - string.count(")") + carryover
            if excess_opening_brackets > 0:
                temporary_character_list = []
                bracket_balance = 0
                index = -1
                while index >= -len(string):
                    character = string[index]
                    temporary_character_list.append(character)
                    if character == ")":
                        bracket_balance -= 1
                    elif character == "(":
                        bracket_balance += 1
                    if bracket_balance == excess_opening_brackets:
                        if character in ILLEGAL_CHARACTERS_FUNCTION_NOMENCLATURE:
                            temporary_character_list.reverse()
                            incomplete_command.append(''.join(temporary_character_list[1:]))
                            break
                        elif index == -len(string):
                            temporary_character_list.reverse()
                            incomplete_command.append(''.join(temporary_character_list))
                            break
                    index -= 1

        else:
            if excess_opening_brackets > 0:
                incomplete_command.append(string)

    # recursively the function will call itself, as long is it notices, that within one of its commands is another
    # command call, as it is indeed possible to use a command call as the parameter of another command as 'deep' as
    # one wants. Copying the command list before, as one cannot edit an iterator during iteration
    _command_list = command_list
    for command in _command_list:
        if stringops.count_ignore_in_quotationmarks(command, "(") > 1:
            command_list += _find_whole_commands(command[command.find("(") + 1:len(command) - 1])

    return command_list


def _find_commands_without_string_parameters(string):
    """
    If given a string, that once came from a terminal input, this function will find every function call within that
    string, under the condition, that within the body (in the brackets) of those functions there is no string. The
    whole function with every parameter and brackets will be put into an unsorted list as a substring.
    The function will also separately append every nested function (functions, that were passed as parameters) at any
    given recursive depth

    EXAMPLE:
    "This(This()) and That()"
    > ["This(This())", "That()", "This()"]

    :param string: (string) the string, that is supposed to contain function calls, without string parameters, that
                            have to get found
    :return: (list) a list of string, that contain the whole function calls with the barcket body
    """
    command_list = []

    # The algorithm will append characters to the temporary string, that is represented by the character list, until
    # it either finds a character, that couldn't be part of a function name or a opening bracket(which is the defining
    # element to identify any function). Upon finding the bracket it'll "switch modes" as indicated by the boolean state
    # variable. In this mode it'll just add every letter to the temp string, since they should be legit as parameters
    # Itll only check for brackets. Whenever it hits an opening bracket it'll ignore the next closing bracket as they'll
    # most likely belong together, but in case it hits a closing bracket, when the "bracket balance" is zero it knows,
    # that the parameter bracket is now finished, so it resets the mode and adds the now gathered temp string to the
    # command list
    temporary_character_list = []
    temporary_string_is_command = False
    bracket_balance = 0
    for character in string:
        temporary_character_list.append(character)

        # breaking the current loop stage when an illegal character has been found
        if character in ILLEGAL_CHARACTERS_FUNCTION_NOMENCLATURE and not temporary_string_is_command:
            temporary_character_list = []
            continue
        if character == "(":
            if temporary_string_is_command:
                bracket_balance -= 1
            else:
                temporary_string_is_command = True
        elif character == ")":
            if temporary_string_is_command:
                if bracket_balance == 0:
                    command_list.append(''.join(temporary_character_list))
                    temporary_character_list = []
                    temporary_string_is_command = False
                    continue
                else:
                    bracket_balance += 1
            else:
                temporary_character_list = []
                continue

    # recursively the function will call itself, as long is it notices, that within one of its commands is another
    # command call, as it is indeed possible to use a command call as the parameter of another command as 'deep' as
    # one wants. Copying the command list before, as one cannot edit an iterator during iteration
    _command_list = command_list
    for command in _command_list:
        if command.count(")") > 1 and command.count("(") > 1:
            command_list += _find_commands_without_string_parameters(command[command.find("(") + 1:len(command) - 1])

    return command_list


def _find_environmental_variables(input_string):
    """
    If given a string, that once came from a terminal input, this function will find every referenced environmental
    variable, that is not part of a string and return a list, containing the string names of there variables
    :param input_string:
    :return:
    """
    variable_list = []
    string_list = stringops.split_string_structures(input_string)
    reg = re.compile("""\$[^'".,()\-+\s=;:]+""")
    for string in string_list:
        if len(string) > 0 and not((string[0] == "'" or string[0] == '"') and (string[-1] == "'" or string[-1] == '"')):
            variable_list += re.findall(reg, string)
    return variable_list


# TODO: make the command folder a parameter
class CommandReferenceDictionary:

    def __init__(self):
        self.dict = {}

        # dynamically calculating the the file path of the "command reference.ini" file, that contains the pickled data
        # of the dictionary used to translate the command names into module names
        config_parser = configparser.ConfigParser()
        config_parser.read("config.ini")
        self.command_directory = config_parser["Paths"]["commands_dir"]
        self.file_path = ''.join([self.command_directory, "/command reference.ini"])
        # loading the config file, containing the reference assignments
        self.reference_parser = configparser.ConfigParser()
        self.reference_parser.read(self.file_path)

        self.dict = dict(self.reference_parser["Commands"])
        print(self.dict)

    # TODO: maybe raise an exception in case there is no command with such a name
    def add(self, command_name, module_name):
        self.dict[command_name] = module_name
        # saving the fresh command, just to be sure
        self.save()

    def get_modulename(self, command_name):
        return self[command_name]

    def is_command(self, command_name):
        return command_name in self.dict.keys()

    def save(self):
        self.reference_parser.write(open(self.file_path, "w"))

    def clear(self):
        self.dict = {}

    def __len__(self):
        return len(self.dict)

    def __getitem__(self, key):
        return self.dict[key]

    def __delitem__(self, key):
        del self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __iter__(self):
        return iter(self.dict.values())