__author__ = 'Jonas'
import unittest
import timeit
import JTSv2.lib.stringutil as strops
import JTSv2.translate as translate


class TestStringUtil(unittest.TestCase):

    def test_split_string_structures(self):
        string = "hallo 'hallo' hallo"
        self.assertEqual(['hallo ', "'hallo'", ' hallo'], strops.split_string_structures(string))

        string = 'This "is" a "test" yay'
        self.assertEqual(["This ", '"is"', " a ", '"test"', " yay"], strops.split_string_structures(string))

        string = """Hello'''This ' should work'''a'"""
        self.assertEqual(["Hello", "'''This ' should work'''", "a'"], strops.split_string_structures(string))

    def test_replace_ignore_quatationmarks(self):
        string = "This will 'This wont'"
        self.assertEqual("X will 'This wont'", strops.replace_ignore_in_quotationmarks(string, "This", "X"))

        string = 'super"""super"""'
        self.assertEqual('X"""super"""', strops.replace_ignore_in_quotationmarks(string, "super", "X"))

        string = "a('Hallo') and b('''a('hallo')''')"
        self.assertEqual("X and b('''a('hallo')''')",strops.replace_ignore_in_quotationmarks(string, "a('Hallo')", "X"))


class TestTranslate(unittest.TestCase):

    def test_find_command_names(self):
        string = "Test(a()) and !Demo('Holy()')"
        self.assertEqual(['Test', 'a', '!Demo'], translate._find_command_names(string))

    def test_find_environmental_variables(self):
        string = "$Hallo = $Nein; '$a'"
        self.assertEqual(['$Hallo', '$Nein'], translate._find_environmental_variables(string))

    def test_translate_environmental_variables(self):
        string = "$Hallo = $No and '$Hallo'"
        self.assertEqual("EnV['$Hallo'] = EnV['$No']; '$Hallo'", translate._translate_environmental_variables(string))

    def test_find_commands_without_string_parameters(self):
        string = "This(This()) and That()"
        self.assertEqual(["This(This())", "That()", "This()"],
                         translate._find_commands_without_string_parameters(string))

        string = "x(a(),b(),c())"
        self.assertEqual(["x(a(),b(),c())", "a()", "b()", "c()"],
                         translate._find_commands_without_string_parameters(string))

    def test_find_whole_commands(self):
        string = "This(This('hallo')) and That('not()')"
        self.assertEqual(["This(This('hallo'))", "That('not()')", "This('hallo')"],
                         translate._find_whole_commands(string))

    def test_translate_commands(self):
        # the test commandreferences
        command_reference = translate.CommandReferenceDictionary()
        command_reference.add("cmd1", "mod1", "command")
        command_reference.add("cmd2", "mod2", "command")

        string = "cmd2(cmd2('hello')) and !cmd1('nothin)') and ?cmd1()"
        result=("import JTSv2.commands.mod1 as mod1\n"
                "import JTSv2.commands.mod2 as mod2\n"
                "mod2.main(self.shell,mod2.main(self.shell,'hello')) and self.background("
                "'''mod1.main(self.shell,'nothin)')''') and help('''mod1''')")
        self.assertEqual(result, translate._translate_commands(string, command_reference))


