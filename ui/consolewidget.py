__author__ = 'Jonas'
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.uix.label import Label
from kivy.clock import Clock

from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty

from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import Python3Lexer
import pygments.token as pygtoken
from pygments.style import Style

import inspect
import time
import os

project_directory = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
from kivy.core.text import LabelBase
LabelBase.register(name="Inconsolata",
                   fn_regular=project_directory+"\\Inconsolata.ttf")



class OrangeStyle(Style):
    default_style = ""
    styles = {
        pygtoken.Comment: "#8F8F8F",
        pygtoken.Keyword: "#FF9500",
        pygtoken.Number: "#3B9696",
        pygtoken.String: "#21D191",
        pygtoken.Name:  "#DEDEDE",
        pygtoken.Name.Variable: "#DEDEDE",
        pygtoken.Name.Function: "#DEDEDE",
        pygtoken.Name.Class: "#DEDEDE",
        pygtoken.Operator: "#FF9500",
        pygtoken.Text: "#DEDEDE",
        pygtoken.Generic: "#DEDEDE",
        pygtoken.Punctuation: "#DEDEDE",
        pygtoken.Escape: "#DEDEDE"
    }


class GreenStyle(Style):
    default_style = ""
    styles = {
        pygtoken.Comment: "#8F8F8F",
        pygtoken.Keyword: "#4B9438",
        pygtoken.Number: "#2AA0B0",
        pygtoken.String: "#2BBD91",
        pygtoken.Name:  "#DEDEDE",
        pygtoken.Name.Variable: "#DEDEDE",
        pygtoken.Name.Function: "#DEDEDE",
        pygtoken.Name.Class: "#DEDEDE",
        pygtoken.Operator: "#4B9438",
        pygtoken.Text: "#DEDEDE",
        pygtoken.Generic: "#DEDEDE",
        pygtoken.Punctuation: "#DEDEDE",
        pygtoken.Escape: "#DEDEDE"
    }


class SimpleConsoleWidget(GridLayout):
    """
    The SimpleConsoleWidget is a kivy Widget meant to emulate a terminal-like experience, consisting of a single
    GridLayout, containing a SimpleConsoleInputLine Widget at the bottom of the window, providing a single line of
    possible command input on default, and a SimpleConsoleOutput widget to display the printed history of command info,
    error, result etc. Messages.

    The console widget supports dynamic syntax highlighting of a python 3 based coding language
    within the input line. The style of this syntax highlighting can either be one of the predefined color schemes of
    this module (orange, green) or any style offered by the pygments module(which also provides the Lexer for Syntax
    highlighting): http://pygments.org/

    The Font used by the input line as well as the output labels is called 'Inconsolata' and is meant to be a modern
    alternative to the old school pixelated console fonts: http://www.levien.com/type/myfonts/inconsolata.html
    The output labels support and encourage the use of kivys markup language to generate colored text and BBCode style
    text anchors

    The input line offers the following additional features, aside from simple text entry:
    - Syntax Highlighting using the Python 3 Lexer, provided by the python module "pygments"(comes with kivy)
    - Multi line code input support. Upon pressing the TAB key the height of the widget will extend by one line and the
      - Pressing the TAB key, when the cursor is positioned right after a ":" will result in a automatic indent of the
        next line. The widget will also keep track of the current indent level, continueing it with every additional new
        line, until the indent is explicitly removed
    - A cache, storing all previously entered commands, that can be scrolled through by pressing the UP and DOWN key,
      with the input line focused, changing the input lines text to be the cached command (a command that has been begun
      will not get lost, but instead be always the latest item of the cache)

    :ivar style: (kivy.ObjectProperty) The pygments style object of which style to be used for syntax highlighting

    :ivar background_shade: (kivy.NumericProperty) The shade of black, which the background of the input line is
    supposed to have. The higher the value, the blacker the background. Ranges from 0 to 1

    :ivar prompt: (kivy.StringProperty) The string, which is to be used as the command prompt of the console
    """
    # the style of syntax Highlighting
    style = ObjectProperty()

    # the background shade of the console
    background_shade = NumericProperty(1)

    # the prompt of the console
    prompt = StringProperty("")

    # the list in which the entered input is being stored
    entered_strings_list = ListProperty([])

    print_buffer = ListProperty([])

    def __init__(self, prompt=">>>", background=1, style="orange", **kwargs):
        # initializing the super class FloatLayout
        super(SimpleConsoleWidget, self).__init__()
        self.cols = 1
        self.padding = 5
        self.spacing = 10
        self.orientation = 'vertical'

        self.prompt = prompt
        self.background_shade = background

        # Setting the syntax Highlighting Style for the terminal input, dependant on the style string passed
        # on default "green", corresponding to GreenStyle
        if style == "green":
            self.style = HtmlFormatter(style=GreenStyle).style
        elif style == "orange":
            self.style = HtmlFormatter(style=OrangeStyle).style
        elif style == "monokai":
            self.style = HtmlFormatter(style="monokai").style
        else:
            self.style = HtmlFormatter(style=GreenStyle).style

        # creating the output component of the condole
        self.output_window = SimpleConsoleOutput()
        self.output_window.size_hint = (1, 0.9)
        self.add_widget(self.output_window)

        # creating the input line of the console
        self.input_line = SimpleConsoleInputLine(prompt=prompt)
        self.input_line.background_shade = self.background_shade - 0.1
        self.input_line.style = self.style
        self.input_line.bind(enter=self.on_text_validate)
        self.add_widget(self.input_line)

        # This is apparently pretty fucking important, its the function that checks if there are any print messages in
        # designated buffer. It has to be done like this because doing the print as the reaction to an event, for
        # for example an observer event of the said buffer will cause some sort of glitch in the ui visibility
        Clock.schedule_interval(self.write_output, 1/30)

    def on_text_validate(self, *args):
        """
        the callback function, that has been bound to the 'enter' variable of the input line and thus is called
        whenever the input line is focused and the enter key is being pressed to validate the text entered as a command
        to be issued.
        :returns: (void)
        """
        entered_string = self.input_line.get_input()
        self.entered_strings_list.append(entered_string)

    def write_output(self, *args):
        try:
            if len(self.print_buffer) > 0:
                self.output_window._print(self.print_buffer.pop(0))
        except:
            pass

    def is_input_available(self):
        """
        returns whether or not there are any entered strings available in the list, that buffers the entered texts until
        used
        :return: (bool) the status od the input buffering list
        """
        return len(self.entered_strings_list) > 0

    def _pop_input_at_index(self, index):
        """
        pops and then returns the item of the entered-inputs-list at the given index, if there is no item at the given
        index returns None instead
        :return:(string) the user entered string
        """
        try:
            return self.entered_strings_list.pop(index)
        except IndexError:
            return None

    def pop_latest_input(self, blocking=False):
        """
        returns the buffered input, that has been entered last and removes it from the list
        :param blocking: (bool) whether or not the method is supposed to block the flow of the program calling or not.
        If False: the method will return None if there was no item to return.
        :return:(string) the user entered string
        """
        if blocking:
            while not self.is_input_available():
                time.sleep(0.0001)
        return self._pop_input_at_index(-1)

    def pop_first_input(self, blocking=False):
        """
        returns the buffered input, that has been entered first and removes it from the list
        :param blocking: (bool) whether or not the method is supposed to block the flow of the program calling or not.
        If False: the method will return None if there was no item to return.
        :return:(string) the user entered string
        """
        if blocking:
            while not self.is_input_available():
                time.sleep(0.0001)
        return self._pop_input_at_index(0)

    def new_label(self):
        """
        Since the output window, displaying the printed text, is not only structured by character layouts such as new
        lines and indents within a single Label, but rather consists of multiple Labels to encapsulate logically
        connected bundles of strings/prints, this method creates a new such Label, onto which the following prints are
        written to.
        """
        self.output_window.new_label()

    def new_command(self, command_string):
        """
        Since the output window, displaying the printed text, is not only structured by character layouts such as new
        lines and indents within a single Label, but rather consists of multiple Labels to encapsulate logically
        connected bundles of strings/prints, this method creates a new such Label, onto which the following prints are
        written to.
        """
        self.output_window.new_label()
        self.println(''.join(["[color=808080][EXECUTING]\n", command_string,
                                             "\n[/color]"]))

    def input_prompt(self, prompt_string, expected_data_type):
        # printing the input prompt
        self.println(prompt_string)
        self.pop_latest_input(blocking=True)
        """
        # rebinding the enter event of the input line, leading the next command to append to a local variable
        input_buffer_list = []
        local_func = lambda *args: input_buffer_list.append(self.input_line.get_input())
        self.input_line.bind(enter=local_func)

        # fetching the newest input as long as the conversion into the expected data type has been successful
        return_input = None
        input_string = None
        while not isinstance(input_string, expected_data_type):
            self.println("Hallo")
            # waiting till the next input is issued and put into the local list
            while len(input_buffer_list) == 0:
                time.sleep(0.0001)
            input_string = input_buffer_list[0]
            try:
                return_input = expected_data_type(input_string)
            except ValueError:
                self.println("The given input is not of the expected data type {}".format(str(expected_data_type)))

        # resetting the enter event binding of the input widget
        self.input_line.bind(enter=self.on_text_validate)

        return return_input
        """

    def print(self, string):
        self.print_buffer.append(string)

    def println(self, string):
        self.print(string+"\n")


class SimpleConsoleComponent(CodeInput):
    """
    The SimpleConsoleComponent is meant to provide a simple base class for the input line widget, defining values and
    methods, that are not necessarily connected to a input lines array of functions in advance, to not clutter a single
    class.

    The SimpleConsoleComponent and therefore the input line as well are based on kivys CodeInput widget.
    :ivar background_shade: (kivy.NumericProperty) the shade of black, which the background of the Widget is supposed to
    have. The higher the value, the blacker the background. Ranges from 0 to 1
    :ivar lexer: (pygments.Lexer) The Lexer to be used for syntax highlighting. Defaults to Python 3
    """
    background_shade = NumericProperty(0.9)

    def __init__(self, background_shade=0.9, **kwargs):
        # Initializing the super class CodeInput
        super(SimpleConsoleComponent, self).__init__()
        # Setting the Python3Lexer for Syntax Highlighting
        self.lexer = Python3Lexer()

        # reversing the value of the background shade, as it is meant to indicate how black the background should be,
        # but in kivy a lesser value means blacker
        self.background_shade = background_shade
        background_color_value = 1 - self.background_shade
        self.background_color = [background_color_value, background_color_value, background_color_value, 1]

        # working around the slight alpha channel animation, that occurs when a TextInput gets the focus, by setting
        # the picture of a normal TextInput as the "animated" picture aswell
        self.background_active = self.background_normal
        self.border = (3, 3, 3, 3)

        # reducing the default font size and changing the font to "Inconsolata".
        # NOTE: Inconsolata is not a part of the default kivy distribution and
        # was downlaoaded at 'http://www.levien.com/type/myfonts/inconsolata.html'
        # For information on how to add custom fonts visit 'http://cheparev.com/kivy-connecting-font/'
        self.font_name = "Inconsolata"
        self.font_size = 13


class SimpleConsoleInputLine(SimpleConsoleComponent):
    """
    The SimpleConsoleInputLine is originally based on the kivy CodeInput and offers the possibility to enter console
    code into a single input line, on default located at the bottom of the ConsoleWidget window.
    The input line offers the following additional features, aside from simple text entry:
    - Syntax Highlighting using the Python 3 Lexer, provided by the python module "pygments"(comes with kivy)
    - Multi line code input support. Upon pressing the TAB key the height of the widget will extend by one line and the
      - Pressing the TAB key, when the cursor is positioned right after a ":" will result in a automatic indent of the
        next line. The widget will also keep track of the current indent level, continueing it with every additional new
        line, until the indent is explicitly removed
    - A cache, storing all previously entered commands, that can be scrolled through by pressing the UP and DOWN key,
      with the input line focused, changing the input lines text to be the cached command (a command that has been begun
      will not get lost, but instead be always the latest item of the cache)

    :ivar max_lines: (kivy.NumericProperty) The maximum amount of lines supported by multiline commands

    :ivar line_count: (kivy.NumericProperty) The counter to keep track of the amount of command lines

    :ivar previous_command_list: (kivy.ListProperty) The list containing the strings of every previous command/
    validated/entered input of the user

    :ivar previous_command_selection_index: (kivy.NumericProperty) The variable keeping track of the index, at which
    the users selection is located within the previous_command_list. changed by pressing UP and DOWN arrow keys

    :ivar indent_count: (kivy.NumericProperty) The counter keeping track of the indent level, at which the users
    multi line command is currently positioned

    :ivar enter: (kivy.NumericProperty) The counter keeping track of the amount of times the enter key has been pressed.
    The knowledge about this count is fairly unimportant, the essential reason for this variable is to bing the
    'on_text_validate' function as its observers callback.

    :ivar prompt: (kivy.StringProperty) The variable holding the string to be used as command prompt
    """
    # The line count to make sure the height of the input Line doesn't exceed the parent widget height
    max_lines = NumericProperty(12)
    line_count = NumericProperty(0)

    # The Cache for previous commands/ validated inputs and the pointer for the index at which the current selection
    # is located relative within the list
    previous_command_list = ListProperty([""])
    previous_command_selection_index = NumericProperty(0)

    # a counting value to keep track of the current indent level of a multiline input. Has to be reset after validate
    indent_count = NumericProperty(0)

    # A counter for the amount of times a input has already been validated. The counter behaviour is not important.
    # mainly serving as the signal for input validation on the ConsoleWidget level
    enter = NumericProperty(0)

    # The prompt for the console input
    prompt = StringProperty("")

    def __init__(self, prompt=">>>", indent_length=4, **kwargs):
        super(SimpleConsoleInputLine, self).__init__(multline=False)
        # setting the height initially to the Font's size and some extra pixels for the borders
        self.height = self.font_size + 14
        # setting the height hint to None, so it is being recessive, when it comes to space distribution, letting the
        # output window get the additional space
        self.size_hint = (1, None)
        # setting the multiline property to False, as it is easier to create the newline in a custom manner and having
        # access to the "on_text_validate" event of the TextInput super class, sending the input text to the processing
        # framework later tied to this ConsoleWidget
        self.multiline = False

        # creating the indent string for multiline inputs
        self.indent_string = " " * indent_length
        # setting the prompt string
        self.prompt = prompt + " "
        self.text = self.prompt

    def get_input(self):
        """
        returns the command, that is currently present within the InputLine, without deleting the command.
        This method has to be used instead of just taking the 'text' property of the widget, because the text property
        inherits things like the prompt and multiline separations.

        EXAMPLE:
        self.text = ">>> hallo"
        > "hallo"

        :return:(string) the content of the InputLine
        """
        # Splitting the the commands into lines and removing the beginning of each line string until the first
        # whitespace, as they are a fundamental part of the prompt as well as the multiline prompts
        command = self.text
        command_lines_old = command.split("\n")
        command_lines_new = []
        for command_line in command_lines_old:
            command_lines_new.append("\n")
            command_lines_new.append(command_line[command_line.find(" ") + 1:])
        return ''.join(command_lines_new[1:]).format()

    def insert_text(self, substring, from_undo=False):
        """
        Function every substring has to pass through when being entered. Not letting the Command prompt be modified by
        adding cahracters to it.
        :param substring:
        :param from_undo:
        :return:
        """
        # Not letting any text be inserted while the cursor is within the prompt string
        if not(self.cursor_row == 0 and self.cursor_col < len(self.prompt)):
            # protecting the command prompt from getting deleted
            return super(SimpleConsoleInputLine, self).insert_text(substring, from_undo=from_undo)
        else:
            return ""

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        The callback method that is called for every keyboard input while the InputLine widget is focused, being the
        core logic method of the widget, executing various functionalities for different key presses:
        - TAB:      Within the Input Widget the tabulator press creates a linebreak for multiline commands(Which one
                    will need with a python based shell language. Limited to ~12 lines). Adding separate prompts for
                    each line and an indent when right after ':'
        - B_SPACE:  simply deleting the last character. Detects whole indent blocks and deletes them in one go.
                    Deletes linebreaks
        - ENTER:    Increments the enter counter, causing the text validate event/callback
        - ARROWS:   Switches the text between the previous commands
        :param window:
        :param keycode: Keycode[1] is the string format of the passed string
        :param text:
        :param modifiers:
        :return: True
        """
        # Keycode[1] is the string format of the passed string

        # Inside the InputLine environment a tab press signals the users need to write a multiline command. Therefore
        # a newline character will be appended to the text and the line count will be incremented by one. In case the
        # tab is pressed, right after a ':' this probably means, the user wants to begin a indented code segment in the
        # next line, so a indent string (how many whitspaces this may be) will be additionally appended to the text
        if keycode[1] == "tab":
            # only adding the newline in case the max amount of lines hasn't yet been reached
            if self.line_count < self.max_lines:
                self.height += (self.font_size + 1)

                newline_string = "\n>>  "
                if self.indent_count > 0:
                    newline_string += self.indent_string * self.indent_count
                if len(self.text) > 0 and self.text[-1] == ":":
                    # in case there was a ':' adding a additional indent. Incrementing indent count
                    newline_string += self.indent_string
                    self.indent_count += 1
                self.text += newline_string
                self.line_count += 1

        # Since defining this specific custom function gets rid of the deletion possibility of the TextInput widget,
        # that behaviour has to be added explicitly. Reducing the height of the input, when deleting a newline
        # character. Reducing the indent_count when deleting a whole indent bl
        elif keycode[1] == "backspace":
            # checking the length first, because the index tended to go out of range and crash
            if len(self.text) > 0:
                # making the difference between the handling of single- and multi-line commands
                if self.cursor_row > 0:
                    if self.cursor_col <= 4:
                        # checking for the character length of the line in which the cursor is currently positioned, and
                        # deleting the line only if there is no content in said line, if there are characters aside from
                        # the prompt deleting nothing
                        if len(self.text.split("\n")[self.cursor_row]) == 4:
                            self.do_cursor_movement("cursor_up")
                            self.do_cursor_movement("cursor_end")
                            self.height -= (self.font_size + 1)
                            self.text = self.text[:-5]
                            self.line_count -= 1
                        else:
                            pass
                    else:
                        self._delete_item_on_backspace()
                else:
                    if self.cursor_col <= 4:
                        pass
                    else:
                        self._delete_item_on_backspace()

        # Upen enter is pressed when the input line is not empty the enter variable is incremented, giving the signal
        # for the Console widget to collect the issued command from he input line
        elif keycode[1] == "enter":
            if len(self.text) > 3:
                if self.text[-1] != ":":
                    self.enter += 1
                    self.text = self.prompt

        elif keycode[1] == "up":

            if len(self.previous_command_list) > self.previous_command_selection_index + 1:
                self.previous_command_selection_index += 1
                self.text = self.previous_command_list[self.previous_command_selection_index]
                # adjusting the height of the widget to the height of the previous command
                self._adjust_height_to_text()
                # setting up the right cursor position
                self.scroll_x = 0
                self.do_cursor_movement("cursor_home")
                for i in range(len(self.prompt)):
                    self.do_cursor_movement("cursor_right")

        elif keycode[1] == "down":
            if self.previous_command_selection_index > 0:
                self.previous_command_selection_index -= 1
                self.text = self.previous_command_list[self.previous_command_selection_index]
                # adjusting the height of the widget to the height of the previous command
                self._adjust_height_to_text()
                # setting up the right cursor position
                self.scroll_x = 0
                self.do_cursor_movement("cursor_home")
                for i in range(len(self.prompt)):
                    self.do_cursor_movement("cursor_right")

        # Moving the cursor around with the arrow keys
        elif keycode[1] == "left" or keycode[1] == "right":
            self.do_cursor_movement("cursor_{0}".format(keycode[1]))

        return True

    def on_text(self, *args):
        """
        Callback for text change event.
        - Updates the first element of the previous command list to be the text currently in the input line.
        :param args:
        :return:
        """
        # Updating the first element of the previous command list to be the current input, so it will be cached saved
        # in case the user decides he wants to continue writing it
        if self.previous_command_selection_index == 0:
            self.previous_command_list[0] = self.text

    def on_enter(self, *args):
        """
        Callback for the enter counter change event. The event of a changed(incremented) enter counter was triggered by
        the user pressing the 'Enter' key, therefore manly signaling the main ConsoleWidget, that the command input
        can now be fetched to be processed further.
        The contents of this method are always executed before extern bound callbacks and include:
        - The just finished entered command will be added to the cache of previous commands
        - All to one temporary input session bound variables like the line count(therefore also the widget height),
          the previous command selection index and the indent level are being reset
        :param args: dunno
        :return: (void)
        """
        # adding the entered input as the second element of the previous commands list, if it isn't already in there
        # Preventing multiple command issues to jam the cache list
        if self.text not in self.previous_command_list[1:]:
            self.previous_command_list.insert(1, self.text)

        # resetting all temporary values of the input line
        self.previous_command_selection_index = 0
        self.height -= self.font_size * self.line_count
        self.line_count = 0
        self.indent_count = 0

    def _adjust_height_to_text(self):
        """
        This function adjusts the height variable of the widget to match the height of the text in the text variable
        :return: (void)
        """
        # calculates the amount of lines, which the widget currently displays, by dividing the absolute height by the
        # height of each line
        current_lines = 1 + ((self.height - (self.font_size + 14)) / (self.font_size + 1))
        # calculates the amount of lines of the text, by the amount of newline characters within
        text_lines = self.text.count("\n") + 1
        # adds the difference of those to the absolute height. Can be negative -> can make it bigger and smaller
        self.height += (text_lines - current_lines) * (self.font_size + 1)

    def _delete_item_on_backspace(self):
        """
        This function manually implements the behaviour for the deletion of characters upon pressing the backspace key
        on the keyboard. without this function, the pressing of the backspace key would either result in nothing or
        independent of the text cursor position just delete the last character.
        This function creates a new string based on the already given string property "text", but leaving out the
        the character, that is located in left to the cursor. Because the cursor would jump to the end of the string or
        in this case end of the input line, the function also implements a manual movement of the cursor to its original
        position to at least make it seem like it hasnt moved in the first place
        :return: (void)
        """
        # saving the original cursor position before the text is being modified
        col = self.cursor_col
        row = self.cursor_row

        necessary_moves = 0
        # checking whether the text of the input line is meant to resemble a single- or multi-line command, as a
        # multiline command would be way harder to process, saving processing power, as most of the commands will
        # be single line anyways
        if row == 0:
            # just renewing the text, but without including the character right in front of the cursor
            self.text = ''.join([self.text[:col - 1], self.text[col:]])

            # since the cursor will snap to the end of the text after the text string has been modified, moving the
            # cursor manually back to its original position to at least make it seem like it stayed there
            if col < len(self.text) + 1:
                necessary_moves = len(self.text[col:])
                for i in range(necessary_moves + 1):
                    self.do_cursor_movement("cursor_left")
        else:
            # splitting the text into its individual lines
            lines = self.text.split("\n")
            # just renewing the text of the line in which the cursor is currently positioned, but without including
            # the character right in front of the cursor
            lines[row] = ''.join([lines[row][:col - 1], lines[row][col:]])
            # adding the linebreak characters to the list and creating a new text string from this list
            newlines = []
            for i in range(len(lines)):
                print(i)
                newlines.append(lines[i])
                newlines.append("\n")
            print(lines)
            print(newlines)
            self.text = ''.join(newlines[:-1])

            # since the cursor will snap to the end of the text after the text string has been modified, moving the
            # cursor manually back to its original position to at least make it seem like it stayed there
            for i in range(len(lines) - row - 1):
                self.do_cursor_movement("cursor_up")

            if col < len(lines[row]) + 1:
                necessary_moves = len(lines[row][col:])
                for i in range(necessary_moves + 1):
                    self.do_cursor_movement("cursor_left")


class SimpleConsoleOutput(ScrollView):
    """
    A widget meant to act as the displaying part of a simple kivy console. Since the widget is a child class of the kivy
    ScrollView, the generated window is scrollable by the mouse wheel, as well as drag and drop and capable of showing
    colored text with kivys Markup tags.

    The widget extends the ScrollView class contains a Gridlayout as only child widget (since the ScrollView cant
    consist of more than one child). Every time the output window is issued to print a logically connected bundle of
    strings (such as a new command being issued), a new MultiLineLabel will be created and added to the internal
    'labels' list. Text will by default only be printed onto the last item of this list, the active label.
    """
    labels = ListProperty([])

    def __init__(self, **kwargs):
        super(SimpleConsoleOutput, self).__init__()
        # Creating the Gridlayout, that'll later contain all the labels, representing the output of the different
        # commands, because the ScrollView itself can only contain one child widget, which will be the layout
        self.grid_layout = GridLayout(cols=1, padding=2, spacing=-2)
        self.grid_layout.size_hint_y = None
        self.grid_layout.size_hint_x = 1
        # This is actually very important, it assigns the minimum height/height of the gridlayout to be constantly
        # updated upon a change has appeared
        self.grid_layout.bind(minimum_height=self.grid_layout.setter("height"))
        self.add_widget(self.grid_layout)

    def _print(self, string):
        """
        adds the text given by 'string' to the text variable of the currently active label of the layout, which is the
        the last label added
        :param string: (string) the content to be printed onto the widget
        :return: (void)
        """
        self.labels[-1].text += string
        self.labels[-1].texture_update()

    def _println(self, string):
        """
        calls the '_print' method, but adds a newline character to the end of the content string
        :param string: (string) the content to be printed onto the next line of the widget
        :return: (void)
        """
        self._print(string + "\n")

    def new_label(self):
        """
        Since the output widget for text display is not only being structured by character layout such as newlines or
        indents, but also by separating every logically connected unit of string prints into a different label, this
        function creates a new such label, to which every following text is being printed on. The Labels reference will
        be stored inside the 'labels' list.
        :return: (void)
        """
        label = MultiLineLabel()
        label.size_hint_y = None
        label.size_hint_x = 1
        label.bind(size=label.setter('text_size'))
        label.height = label.text_size[1] + 10
        label.markup = True
        label.halign = "left"

        # reducing the default font size and changing the font to "Inconsolata".
        # NOTE: Inconsolata is not a part of the default kivy distribution and
        # was downlaoaded at 'http://www.levien.com/type/myfonts/inconsolata.html'
        # For information on how to add custom fonts visit 'http://cheparev.com/kivy-connecting-font/'
        label.font_name = "Inconsolata"
        label.font_size = 13

        self.grid_layout.add_widget(label)
        self.labels.append(label)

    def input_prompt_issued(self):
        if len(self.labels) >= 1 and len(self.labels[-1].text) >= 1:
            lines_last_label = self.labels[-1].text.split("\n")
            if len(lines_last_label) >= 1:
                return "[INPUT]" in lines_last_label[-2] or "[IN]" in lines_last_label[-2]
        return False


class MultiLineLabel(Label):
    """
    Copied from stackexchange.com, due to sincere frustration.
    A kivy Label, with the additional feature of updating its own height, after the text has been modified to eventually
    generate a new line, crossing the widget borders.
    """
    def __init__(self, **kwargs):
        super(MultiLineLabel, self).__init__()
        self.text_size = self.size
        self.bind(size= self.on_size)
        self.bind(text= self.on_text_changed)
        self.size_hint_y = None # Not needed here

    def on_size(self, widget, size):
        """
        i have no clue what happens here, but apparently it updates the height of the Label to match its text height
        even during runtime and dynamic text contents
        :param widget:
        :param size:
        :return:
        """
        self.text_size = size[0], None
        self.texture_update()
        if self.size_hint_y is None and self.size_hint_x is not None:
            self.height = max(self.texture_size[1], self.line_height)
        elif self.size_hint_x is None and self.size_hint_y is not None:
            self.width  = self.texture_size[0]

    def on_text_changed(self, widget, text):
        self.on_size(self, self.size)