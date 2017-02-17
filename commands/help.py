import JTSv2.commands.cutil as cutil

import configparser
import importlib
import inspect
import os

COLOR_DICT = {
    "white": "DEDEDE",
    "red": "D61818",
    "green": "3AD126",
    "blue": "397AD4",
    "magenta": "D439B7"
}


def main(shell, *args):
    """
    This command is used to get help for the different commands the shell has access to. One or multiple string
    arguments with command names can be supplied to this function and in return the docstrings to those commands will
    be displayed. In case there is no argument a list of all the available commands and their description will be
    printed.

    Args:
        shell: -
        *args:

    Returns:
    The string containing the help information
    """
    # First of all making the decision of whether arguments have been passed to the function or not.
    # In case no arguments have been passed to the function, it will display a list of all the possible commands
    # available in the shell, if an argument was passed it will display the complete docstring of this command
    args = list(args)
    command_reference = cutil.get_default_command_reference()

    if len(args) == 0:
        # Getting the command list for all the commands according to the default command reference dict
        command_list = get_command_list(command_reference)

        # Getting the list of the description strings to those commands
        description_string_list = get_description_string_list(command_list, command_reference)

        # Getting the formatted string to print to the shell
        help_string = get_help_string_listing_format(command_list, description_string_list)

        shell.print_info(help_string)
    else:
        # In case there actually are specific parameters to the help function, it is also possible, that the help is
        # supposed to be displayed for more than just one command, therefore looping thorugh the list of the passed
        # arguments ans assembling the final help string as the sum of the individual command help strings
        string_list = ["\n"]
        for arg in args:
            # The argument has to be string
            if isinstance(arg, str):
                # Getting the command name as the string that was passed and the doc string derived from that name using
                # the designated function for that
                command_name = str(arg)
                doc_string = get_doc_string(command_name, command_reference)

                # Building the help string for the command
                help_string = get_help_string_single_format(command_name, doc_string)
                string_list.append(help_string)
                string_list.append("\n")

        # Assembling the string list into the final help string an printing it
        help_string = ''.join(string_list)
        shell.print_info(help_string)


def get_doc_string(command_name, command_reference_dict):
    """
    This function gets the help string for any given (valid) command of the shell system, by getting the corresponding
    module name of the module within the commands folder from the passed command reference dictionary, dynamically
    importing that module and then extracting the doc string of the 'main' function of that module
    Args:
        command_name: The string name of the command, whose doc string to get
        command_reference_dict: The dictionary whose command name - module name translation information shall be used
            as foundation for the look up

    Returns:
    The original doc string of the command, whose name has been passed
    """
    # Getting the actual module name from the command reference dictionary, by passing it the command name
    module_name = command_reference_dict[command_name]

    # Dynamically importing the module to the to the corresponding command name, which is supposed to be in the
    # 'commands' folder of this very project
    import_string = "JTSv2.commands.{}".format(module_name)
    module = importlib.import_module(import_string)

    # Calling the function that returns the doc string of an object on the main function of the module, that has just
    # been imported. The function assumes, that the module has a main function, because that is the main premise for
    # the command working, as the shell always executes this function for every module as the actual function behind
    # each command call
    return inspect.getdoc(module.main)


def get_doc_string_list(command_list, command_reference_dict):
    """
    Gets the doc string for each command, whose command name is part of the passed list, using the given command
    reference dictionary to identify the module names, assigned to the commands, to know in which file of this project
    to fetch the string form
    Args:
        command_list: A List containing the string names of all the jts commands whose help strings are requested
        command_reference_dict: A dictionary assigning the string names of jts commands, as they can be used in the
            shell to string names of the modules, that actually contain the function/source code to those
            according commands

    Returns:
    A list of the doc strings, that were written for the python functions, belonging to the commands given by the passed
    list. The list of doc strings will be the same length and same order as the command name list.
    """
    # This list will contain all the help strings in the same order as the commands are aligned in the passsed list,
    # which is being used as the basis of this function
    doc_string_list = []
    for command_name in command_list:
        # Getting the doc string for the command, whose command name ist the current item of the loop and appending the
        # doc string to the list
        doc_string = get_doc_string(command_name, command_reference_dict)
        doc_string_list.append(doc_string)

    # Returning the resulting list
    return doc_string_list


def get_description_string(doc_string):
    """
    Extracts the string, that really only contains the short description of a python docstring in Google Style Format.
    Args:
        doc_string: The string of the docstring of a function

    Returns:
    The string, that only contains the description of the funtion/command
    """
    # The description is considered to be the part of the help string, that comes first and provides a basic overview
    # about the functions/commands functionality, but does not include information about the parameters or the
    # return of the function

    keyword_list = ["Args:", "Returns:", "Raises:", "Notes:", "See Also:", "Attributes:", "Warnings:"]

    # Splitting the doc string into its individual lines, because each line is being checked if it starts with any one
    # of the those keywords, in case it does not the line is being added to the description string, in case it does
    # the description string, that has been assembled up to that point will be instantly returned
    doc_string_lines = doc_string.split("\n")
    description_string_list = []

    for line in doc_string_lines:

        if len(line) == 0:
            continue
        # The function can be more effective by not checking every single line for all the different keywords, but
        # pre selecting, which line could potentially be a keyword and which cant. Since in the Google docstring
        # format begins with an upper case letter it is save to assume, that a line beginning with a lower case
        # letter does not have to be checked.
        if line[0].islower():
            description_string_list.append(line)
            continue

        # Also every keyword has to be followed by a double point, so if a line does not contain such a double point at
        # all, it is also safe to assume that this is not
        if not(":" in line):
            description_string_list.append(line)
            continue

        for keyword in keyword_list:
            if keyword in line:
                # In case the keyword is in the line, it can still be the case, that it is part of the description,
                # therefore it has to be confirmed, by checking whether or not the Keyword is at the beginning of the
                # line or not
                if line[0:len(keyword)] == keyword:
                    # In case there indeed is a keyword in the line, this means, that the basic description has to be
                    # over at this point, thus instantly returning the string, that has been collected inside the
                    # 'description_string_list' up until now
                    description_string = ''.join(description_string_list)
                    return description_string

        # In case the doc string actually did not contain any keywords, returning essentially the whole string after
        # the loop ended, although that is probably not going to happen
        return ''.join(description_string_list)


def get_description_string_list(command_list, command_reference_dict):
    """
    Creates a list with the descriptions of the shell commands extracted from their respective modules, more
    specifically the doc strings of the main methods od those modules, if given the command list of all the commands to
    extract the descriptions for and the command reference dictionary, which holds the string name references of the
    command names as they are used in the shell environment and the actual module names the functions are located in.
    Args:
        command_list:
        command_reference_dict:

    Returns:
    A list with only the description strings of the doc strings of the functions for all the commands, that were given
    by the passed command list. The returned list is sorted, it has the same order as the passed command list.
    """
    # Getting the list of all the dic strings first as they are needed for the process of extracting the pure command
    # description for a given command. The list is in the same order as the command list
    doc_string_list = get_doc_string_list(command_list, command_reference_dict)

    # This list will be extended by the description strings for each command in the same order as the command list and
    # the doc string list
    description_string_list = []
    for doc_string in doc_string_list:
        if doc_string is not None:
            description_string = get_description_string(doc_string)
            description_string_list.append(description_string)
        else:
            description_string_list.append("None")

    return description_string_list


def get_command_list(command_reference_dict):
    """
    If given the a command reference dictionary, being the object, the shell system uses to resolve its commands and
    translate the command names back into the module names, that actually contain the functionality/code to perform the
    action, that is promised by the command, the function will return a list with all the command names (not being the
    module names of the commands folder!)
    Args:
        command_reference_dict: A dictionary, that assigns the string names of the commands as they can be used inside
            the shell environment(keys) to those string names of the modules within the commands folder, that actually
            correspond to the functionality of those commands.

    Returns:
    Returns a list, that contains the string names of all the commands, as the can be entered into the Shell terminal
    to achieve some kind of action. (Those string names do not have to directly correspond with the module names)
    """
    # Setting the keys of that dict to be the command list
    command_list = list(command_reference_dict.keys())
    command_list.sort()
    return command_list


def get_help_string_listing_format(command_list, description_string_list, spacing=1, color="green", plain=False):
    """
    If given the list of commands for which the general help function is requested and the list of the respective
    description strings of the doc strings of those functions, this function assembles the both list into a formatted
    string, which can be directly printed to the shell. The format includes the command names being sort of headers
    for their description and all those packages of command name and description are being written underneath each
    other with a specific spacing

    Args:
        command_list: The list, which is meant to contain all the strings of the command names to the entirety of
            commands for which the help is requested
        description_string_list: The list, containing all the strings of the descriptions to those commands for which
            the help is requested. The dimension of this list has to match with the command list or an exception will
            be thrown. Also the order has to match with the respective commands in their list otherwise resulting
            false output
        spacing: The integer amount of line breakes/space between two command help strings. On default 1
        color: The string resembling the color in which the command name should be highlighted above the description
            in the shells print. The different color strings can be seen in the dictionary within the help module.
            'green on default'
        plain: The boolean parameter of whether the string should be plain or not, meaning whether the kivy color
            format for the command names should be applied or not. False on default

    Returns:
    the help string
    """
    # The exception for when the command_list and the description list dont match in size
    if len(command_list) != len(description_string_list):
        raise IndexError("The list of the dimension doesnt match the one of their respective descriptions for the "
                         "formatting of the help command print")

    # In the first step creating a list, which contains the command name as a sort of header, then a line break, the
    # description string to the according command another line break and then as many line breaks as there is
    # specified by the spacing parameter of the function.
    string_list = ["THE COMMAND DESCRIPTIONS\n"]

    # Going by the index, as the two lists should be(!) the same length and order
    for index in range(0, len(command_list)):

        # Adding the string of the command name first. If the plain parameter(boolean) is True, this string will be the
        # plain string only, if it is False though the string will be kivy formatted to be the chosen color.
        command_name = command_list[index]
        if not plain:
            color_string = COLOR_DICT[color]
            command_name = "[color={}]{}[/color]".format(color_string, command_name)
        string_list.append(command_name)
        string_list.append("\n")

        # Adding the actual description string for the command, that actually contains the relevant information
        description_string = description_string_list[index]
        string_list.append(description_string)
        string_list.append("\n")

        # Adding as much line breaks as specified by the integer parameter 'spacing'
        for i in range(0, spacing):
            string_list.append("\n")

    # In the second step, combining the just created list of sub strings to one single string and returning it
    help_string = ''.join(string_list)
    return help_string


# EXTEND THE FORMATTING FUNCTIOMNALITY OF THIS FUNCTION TO MAKE PRINT LOOK BETTER SOME DAY
def get_help_string_single_format(command_name, doc_string, color="green", plain=False):
    """
    This function simply assembles the string of a command and its doc string, so that the name is displayed as sort of
    colored header to the actual docstring underneath as one single formatted string.

    Args:
        command_name: The string name of the command for which the help is supposed to be displayed
        doc_string: The doc string to the according command
        color: The string resembling the color in which the command name should be highlighted above the description
            in the shells print. The different color strings can be seen in the dictionary within the help module.
            'green' on default
        plain: The boolean parameter of whether the string should be plain or not, meaning whether the kivy color
            format for the command names should be applied or not. False on default

    Returns:
    The formatted doc string
    """
    # The list, which will later be assembled into the string
    string_list = []

    # First checking for the boolean 'plain' parameter, if it is True, than the command name will just be displayed
    # as any other normal string, otherwise it will be kivy formatted to be the color as dictated by the parameter
    if not plain:
        color_string = COLOR_DICT[color]
        command_name_colored = "[color={}]{}[/color]".format(color_string, command_name)
        string_list.append(command_name_colored)
    else:
        string_list.append(command_name)
    string_list.append("\n")

    # Adding the docstring to the list as it is
    string_list.append(doc_string)
    string_list.append("\n")

    # Joining the list into one single string and then returning it
    help_string = ''.join(string_list)
    return help_string




