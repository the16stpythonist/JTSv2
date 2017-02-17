import os
import time
import multiprocessing


def main(shell):
    """
    This command restarts the whole shell system, which means stopping the main shell server, every shell thread and
    every running process, which also means terminating all programs, that have been started by the shell system
    Args:
        shell: -

    Returns:
    void
    """
    multiprocessing.Process(target=call_restart, args=[shell.project_path,]).start()
    shell.stop_all()


def call_restart(project_path):
    time.sleep(0.5)
    bat_path = "{}\\start_jts_server.bat".format(project_path)
    command = "{}".format(bat_path)
    os.system(command)
