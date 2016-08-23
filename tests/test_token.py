__author__ = 'Jonas'
import unittest
import JTShell2.JTSv2.tokens as t


class TestParameterConversionFunctions(unittest.TestCase):

    def test_convert_parameter_string(self):
        self.assertEqual("hello", t.convert_parameter_string('''"hello"'''))
        self.assertEqual("hello", t.convert_parameter_string("'hello'"))
        self.assertEqual('''"hello"''', t.convert_parameter_string('''""hello""'''))
        self.assertRaises(ValueError, t.convert_parameter_string, "hello")

    def test_convert_parameter_number(self):
        self.assertEqual(400.0, t.convert_parameter_number("400"))
        self.assertEqual(400.0, t.convert_parameter_number("400.0"))
        self.assertEqual(23.1234, t.convert_parameter_number("23.1234"))
        self.assertRaises(ValueError, t.convert_parameter_number, "hello")

    def test_convert_parameter_list(self):
        self.assertEqual([1, 2, 3], t.convert_parameter_list("[1,2,3]"))
        self.assertEqual(["hallo", 2, "!"], t.convert_parameter_list('''[ "hallo" , 2,"!" ]'''))
        self.assertEqual([[1, 1], [1, 1]], t.convert_parameter_list("[[1,1],[1,1]]"))
        self.assertRaises(ValueError, t.convert_parameter_list, "[1, 2")

    def test_remove_whitespace_before_after(self):
        self.assertEqual("a", t.remove_whitespace_before_after(" a "))
        self.assertEqual("a", t.remove_whitespace_before_after(" a"))
        self.assertEqual("a", t.remove_whitespace_before_after("a"))
        self.assertEqual("a a", t.remove_whitespace_before_after("a a"))
        self.assertEqual("aaa aa aa aaaaa", t.remove_whitespace_before_after("   aaa aa aa aaaaa     "))

    def test_split_parameter_list(self):
        self.assertEqual(["1", "2", "3"], t._split_parameter_list("[1,2,3]"))
        self.assertEqual(["[2]", "2"], t._split_parameter_list("[[2],2]"))
        self.assertEqual(["['q']", "['q']"], t._split_parameter_list("[['q'],['q']]"))


class TestParameterToken(unittest.TestCase):

    def test_construction(self):
        parameter1 = t.ParameterToken("hello", "'this is a string type '")
        self.assertEqual(parameter1.get_name(), "hello")
        self.assertEqual(parameter1.get_value(), "this is a string type ")

        parameter2 = t.ParameterToken("integer", "400")
        self.assertEqual(parameter2.get_name(), "integer")
        self.assertEqual(parameter2.get_value(), 400.0)

        parameter3 = t.ParameterToken("list", "[[1,2,3],[1,[1]]]")
        self.assertEqual(parameter3.get_value(), [[1, 2, 3], [1, [1]]])


class TestFunctionToken(unittest.TestCase):

    args = ["p1", "p2", "p3"]
    function1 = t.FunctionToken("func1(p1=1,p2=2,p3=3)")

    def test_construction(self):
        self.assertEqual("func1", self.function1.name)

    def test_layer(self):
        self.assertTrue(self.function1.is_foreground())
        self.assertFalse(self.function1.is_background())

    def test_get_parameters(self):
        self.assertEqual(self.args, self.function1.get_parameter_names())
        self.assertEqual(self.args[0], self.function1.get_parameter(self.args[0]).get_name())
        self.assertRaises(IndexError, self.function1.get_parameter, "hello")
        # adding an additional parameter
        self.function1.add_parameter(t.ParameterToken("new_parameter", "'infinite'"))
        self.assertEqual("infinite", self.function1.get_parameter_value("new_parameter"))

    def test_string(self):
        function2 = t.FunctionToken("func(hello=20.0,a=1.0)")
        self.assertEqual("func(hello=20.0,a=1.0)", function2.get_string())

    def test_split_parameter_string(self):
        self.assertEqual(t.FunctionToken._split_parameter_string("hello='hello'", "="), ["hello", "'hello'"])
        self.assertEqual(t.FunctionToken._split_parameter_string("hello='not=easy'", "="), ["hello", "'not=easy'"])
        self.assertEqual(t.FunctionToken._split_parameter_string("100", "="), ["100"])
        self.assertEqual(t.FunctionToken._split_parameter_string("hello=func(a='hello')", "="),
                         ["hello", "func(a='hello')"])

