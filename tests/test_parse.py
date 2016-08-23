__author__ = 'Jonas'
import unittest
import JTSv2.parse as parse
import JTSv2.tokens as tokens
import JTSv2.JTLib.JTUtility.list as listop


class TestParsing(unittest.TestCase):

    def test_get_first_token_string(self):
        self.assertEqual(parse._get_first_token_string(" into that"), ("into", " that"))
        self.assertEqual(parse._get_first_token_string("nif a(a='a')"), ("nif", " a(a='a')"))
        self.assertEqual(parse._get_first_token_string("b(b=1) into a(a=1)"), ("b(b=1)", " into a(a=1)"))
        self.assertEqual(parse._get_first_token_string("b(b=')') into a(a=1)"), ("b(b=')')", " into a(a=1)"))

    def test_multi_indices(self):
        self.assertEqual(listop.multi_indices([0, 0, [0, [0]]], 2, 1), [0])

    def test_get_token_from_string(self):
        token1 = parse._get_token_from_string("into")
        self.assertIsInstance(token1, tokens.SyntaxToken)
        self.assertEqual(token1.is_into(), True)
        token2 = parse._get_token_from_string("function('hello', a='=)', b=200 )")
        self.assertIsInstance(token2, tokens.FunctionToken)
        self.assertEqual(token2.get_name(), "function")
        self.assertEqual(token2.get_parameter_names(), ["REQUIRED", "a", "b"])
        self.assertEqual(token2.get_parameter_value("a"), "=)")

    def test_parse(self):
        command1 = "func1('hello', param=func2(a=2))"
        tree1 = parse.parse(command1)
        self.assertIsInstance(tree1.list[0], tokens.FunctionToken)
        self.assertEqual(tree1.list[0].get_name(), "func1")
        self.assertEqual(tree1.list[0].get_parameter_names(), ["REQUIRED", "param"])
        self.assertIsInstance(tree1.list[0].get_parameter_value("param"), tokens.FunctionToken)

        command2 = "func('hello)') into (a(a=1) and a(a=1))"
        tree2 = parse.parse(command2)
        self.assertIsInstance(tree2.list[0], tokens.FunctionToken)
        self.assertIsInstance(tree2.list[1], tokens.SyntaxToken)
        self.assertTrue(tree2.list[1].is_into())
        self.assertIsInstance(tree2.list[2], list)
        self.assertIsInstance(tree2.list[2][2], tokens.FunctionToken)

        command3 = "HELLO = 100"
        tree3 = parse.parse(command3)
        self.assertIsInstance(tree3.list[0], tokens.VariableToken)
        self.assertIsInstance(tree3.list[2], tokens.DataTypeToken)
        self.assertEqual(tree3.list[2].value, 100.0)

