

def main(shell, argument):
    """
    This function simply prints the argument, that was passed to this command as a string into the display of the
    terminal.

    Args:
        shell: -
        argument: Any object, that can be converted into a string

    Returns:
    void
    """
    shell.print_info(str(argument))
