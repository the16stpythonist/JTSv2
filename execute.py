__author__ = 'Jonas'
import pickle
import inspect
import os
import JTSv2.datamanage as datamanage
import JTSv2.process as process

PROGRAM = "program"
COMMAND = "command"


# TODO: Create naming algorithm processes
def execute(shell, translated_string):
    """
    When given the shell and the already translated string of the code to be executed, this function provides the
    namespace containing the variables, having exactly those names, that have been assumed by the translation process
    and then dynamically executes the code within translated_string, using the python interpreter itself
    :param shell: (Shell) The reference to the shell instance, that issued the execute function
    :param translated_string: (string) The already translated string, containing only pure valid python expressions/
    statements
    :return: (void)
    """
    # ALL VARIABLE NAMES ARE IMPORTANT AS TEY ARE PART OF THE TRANSLATION PROCESS AND HAVE TO BE CHANGED THERE AS WELL

    # creating the foreground ShellCom interface for execution
    fg_com = datamanage.ForegroundShellCom(shell.shell_server, shell)

    # shortening the name of the environmental variable container, as the term 'EnV' is used within the translated
    # string to be dynamically executed, therefore the variable container has to be available in this local namespace
    EnV = shell.env_variable_container
    process_list = shell.process_list
    try:
        compiled_input = compile(translated_string, '<string>', 'exec')
        exec(compiled_input)
    except Exception as e:
        fg_com.print_error(e)


# TODO: make it return subprocess alive, add a method for checking to the ProcessList
def background(shell, execution_statement):
    """
    In charge of executing the background commands, marked by the exclamation mark syntax "!command()", by simply
    paasing the execution statement(translated code) to the shells process list, which is starting a new process, that
    basically does a very similar dynamic execution as the 'execute' function, only within a multiprocessing subprocess,
    so the execution wont stop the work flow of this python instance.
    :param shell: (Shell)
    :param execution_statement: (string) The already translated string, containing only pure valid python expressions/
    statements
    :return: (void)
    """
    shell.process_list.start_process(execution_statement, shell.shell_server.data_nexus)











