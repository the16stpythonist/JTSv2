__author__ = 'Jonas'
import unittest
import pickle
import JTSv2.tokens as tokens
import JTSv2.process as process
import JTSv2.execute as execute
import JTSv2.parse as parse


class TestProcessCommunication(unittest.TestCase):

    def test_communication(self):
        function_token = tokens.FunctionToken("test(a=1)")
        self.assertEqual(function_token.name, "test")
        self.assertEqual(function_token.get_parameter_value("a"), 1)
        process_object = process.Process(function_token, (12025, 12035))
        return_token = process_object.wait_return()
        self.assertIsInstance(return_token, tokens.ReturnToken)
        self.assertEqual(return_token.return_value, 1)
        self.assertEqual(return_token.exit_code, True)

    def test_pickle(self):
        return_token = tokens.ReturnToken(1, True)
        self.assertIsInstance(return_token, tokens.ReturnToken)
        return_token_pickled = pickle.dumps(return_token)
        print(return_token_pickled)
        return_token = pickle.loads(return_token_pickled)
        self.assertIsInstance(return_token, tokens.ReturnToken)
        self.assertEqual(return_token.return_value, 1.0)


class TestVariableContainer(unittest.TestCase):

    variable_container = execute.VariableContainer("variables")

    def test_construction(self):
        self.variable_container["test_variable"] = 120
        self.assertEqual("test_variable" in self.variable_container.keys(), True)
        self.assertEqual(self.variable_container["test_variable"], 120)

    def test_save_load_variables(self):
        self.variable_container["test_variable"] = 100
        self.variable_container.save_variables()
        self.variable_container.clear()
        self.assertEqual(len(self.variable_container), 0)
        self.variable_container.load_variables()
        self.assertGreater(len(self.variable_container), 0)
        self.assertEqual(self.variable_container["test_variable"], 100)


class TestExecution(unittest.TestCase):

    process_list = process.ProcessList()
    variable_container = execute.VariableContainer("variables")

    def test_simple_execute(self):
        token_tree = parse.parse("test(a=1)")
        self.assertIsInstance(token_tree[0], tokens.FunctionToken)
        #return_token = execute.execute(token_tree, self.process_list, self.variable_container)
        #self.assertIsInstance(return_token, tokens.ReturnToken)
        #self.assertEqual(return_token.return_value, 1.0)