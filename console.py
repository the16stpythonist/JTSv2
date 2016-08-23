__author__ = 'Jonas'
import JTSv2.lib.kivyutil as kivyutil
kivyutil.init_kivy()
from JTSv2.ui.consolewidget import SimpleConsoleWidget
from JTSv2.datamanage import ResultMessage
from kivy.clock import Clock
from kivy.app import App

import inspect
import os


class ShellConsoleWidget(SimpleConsoleWidget):

    def __init__(self, input_queue, output_queue, **kwargs):
        super(ShellConsoleWidget, self).__init__(**kwargs)
        self.input_queue = input_queue
        self.output_queue = output_queue

        # Scheduling the checking of the input queue for any new messages
        Clock.schedule_interval(self.write_pipe_output, 1/30)

    def write_pipe_output(self, *args):
        try:
            message = self.input_queue.get(block=False)
            print(message)
            self.println(message.get_kivy())
        except:
            pass

    def on_text_validate(self, *args):
        super(ShellConsoleWidget, self).on_text_validate(*args)
        if not self.output_window.input_prompt_issued():
            self.new_command(self.input_line.get_input())
        self.output_queue.put(self.input_line.get_input())


class ConsoleApp(App):

    def __init__(self, input_queue, output_queue, **kwargs):
        super(ConsoleApp, self).__init__(**kwargs)
        self.input_queue = input_queue
        self.output_queue = output_queue

    def build(self):
        return ShellConsoleWidget(self.input_queue, self.output_queue)


def main(inp, out):
    ConsoleApp(inp, out).run()
