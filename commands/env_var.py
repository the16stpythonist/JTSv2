# The command of this module is supposed to be able to inspect the env variables of the terminal system
# More specifically, the in case no argument is given, displaying a list of all variables and for specific


def main(shell, arg=None, show_size=True):
    """
    This command provides informational service for the environmental variables of the shell system. In case no
    parameter is passed to the command a table of all available variables is printed. In case a string, that is not
    a variable name is passed a table for each variable name starting with that substring and a table with all variables
    containing the substring (not necessarily at the beginning) are printed. The tables contain the variable name, the
    type of the variable and the size in bytes. In case a string variable name is passed to the command, a specific
    information is printed, additionally containing the actual content of the variable.
    Args:
        shell: -
        arg: Default to None. Substring or string for the name of a variable
        show_size: The boolean value of whether or not the size of the variable is supposed to be printed

    Returns:
    void
    """
    if arg is None:
        # in case the parameter 'arg' is None, the user did not enter a parameter for the command call. In this case
        # a table of all environmental variables is printed
        variable_dict = shell.variables_starting_with("")
        string = shell.get_variables_kivy_string(variable_dict, show_size=show_size)
        shell.print_info(string)
    elif isinstance(arg, str):
        # In case the parameter is a string it could either be an actual variable name or not.
        # In case the string is not a valid variable name tables of variables starting with the substring and containing
        # the substring ara presented to help finding the variable one is looking for
        if arg in shell.keys():
            string = shell.variable_kivy_info(arg)
            shell.print_info(string)
        else:
            string_list = list(["\nVariables starting with the string:"])
            starting_dict = shell.variables_starting_with(arg)
            starting_string = shell.get_variables_kivy_string(starting_dict, show_size=show_size)
            string_list.append(starting_string)
            # Creating the dictionary of all the variables only containing the substring and removing all the entries
            # of all the variable names also starting with the substring
            containing_dict = shell.variables_containing_substring(arg)
            for key in starting_dict.keys():
                if key in containing_dict:
                    del containing_dict[key]
            # Only actually printing the table for the containing dict, if there actually is an item in there
            if len(containing_dict) != 0:
                string_list.append("\nVariables containing the substring:")
                string_list.append(shell.get_variables_kivy_string(containing_dict, show_size=show_size))
            shell.print_info(''.join(string_list))


def get_variable_string(shell, variable_name):
    """
    The function gets the string representation of the variable given by the name
    Args:
        shell: the ShellCom object, through which the environmental variables can be accessed
        variable_name: The string name of the variable in the terminal system

    Returns:
    The string content of the variable
    """
    # accessing the variable through the shell and returning the string format of the variable
    return str(shell[variable_name])


def get_variable_type(shell, variable_name):
    """
    The function gets the string format of the type of the variable
    Args:
        shell: The ShellCom object, through which the environmental variables can ve accessed
        variable_name: The string name of the variable in the terminal system

    Returns:
    The type of the variable
    """
    # Accessing the variable through the shell and returning the string format of the type
    return type(shell[variable_name])
