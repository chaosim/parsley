from textwrap import dedent
from twisted.trial import unittest

from pymeta.builder import TreeBuilder, writePython

def dd(txt):
    return dedent(txt).strip()


class PythonWriterTests(unittest.TestCase):
    """
    Tests for generating Python source from an AST.
    """


    def setUp(self):
        """
        Create a L{PythonBuilder}.
        """

        self.builder = TreeBuilder("BuilderTest")


    def test_exactly(self):
        """
        Test generation of code for the 'exactly' pattern.
        """

        x = self.builder.exactly("x")
        self.assertEqual(writePython(x),
                         dd("""
                            _G_exactly_1 = self.exactly('x')
                            _G_exactly_1
                            """))



    def test_apply(self):
        """
        Test generation of code for rule application.
        """

        x = self.builder.apply("foo", "main", "1", "x")
        self.assertEqual(writePython(x),
                         dd("""
                            _G_python_1 = eval('1', self.globals, _locals)
                            _G_python_2 = eval('x', self.globals, _locals)
                            _G_apply_3 = self.apply("foo", _G_python_1, _G_python_2)
                            _G_apply_3
                            """))



    def test_superApply(self):
        """
        Test generation of code for calling the superclass' implementation of
        the current rule.
        """

        x = self.builder.apply("super", "main", "1", "x")
        self.assertEqual(writePython(x),
                         dd("""
                            _G_python_1 = eval('1', self.globals, _locals)
                            _G_python_2 = eval('x', self.globals, _locals)
                            _G_apply_3 = self.superApply("main", _G_python_1, _G_python_2)
                            _G_apply_3
                            """))


    def test_many(self):
        """
        Test generation of code for matching zero or more instances of
        a pattern.
        """

        xs = self.builder.many(self.builder.exactly("x"))
        self.assertEqual(writePython(xs),
                         dd("""
                            def _G_many_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            _G_many_2 = self.many(_G_many_1)
                            _G_many_2
                            """))


    def test_many1(self):
        """
        Test generation of code for matching one or more instances of
        a pattern.
        """

        xs = self.builder.many1(self.builder.exactly("x"))
        self.assertEqual(writePython(xs),
                         dd("""
                            def _G_many1_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            _G_many1_2 = self.many(_G_many1_1, _G_many1_1())
                            _G_many1_2
                            """))



    def test_or(self):
        """
        Test code generation for a sequence of alternatives.
        """

        xy = self.builder._or([self.builder.exactly("x"),
                               self.builder.exactly("y")])
        self.assertEqual(writePython(xy),
                         dd("""
                            def _G_or_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            def _G_or_2():
                                _G_exactly_1 = self.exactly('y')
                                return _G_exactly_1
                            _G_or_3 = self._or([_G_or_1, _G_or_2])
                            _G_or_3
                            """))

    def test_singleOr(self):
        """
        Test code generation for a sequence of alternatives.
        """

        x1 = self.builder._or([self.builder.exactly("x")])
        x = self.builder.exactly("x")
        self.assertEqual(writePython(x), writePython(x1))


    def test_optional(self):
        """
        Test code generation for optional terms.
        """
        x = self.builder.optional(self.builder.exactly("x"))
        self.assertEqual(writePython(x),
                         dd("""
                            def _G_optional_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            def _G_optional_2():
                                pass
                            _G_or_3 = self._or([_G_optional_1, _G_optional_2])
                            _G_or_3
                            """))


    def test_not(self):
        """
        Test code generation for negated terms.
        """
        x = self.builder._not(self.builder.exactly("x"))
        self.assertEqual(writePython(x),
                         dd("""
                            def _G_not_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            _G_not_2 = self._not(_G_not_1)
                            _G_not_2
                            """))


    def test_lookahead(self):
        """
        Test code generation for lookahead expressions.
        """
        x = self.builder.lookahead(self.builder.exactly("x"))
        self.assertEqual(writePython(x),
                         dd("""
                            def _G_lookahead_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            _G_lookahead_2 = self.lookahead(_G_lookahead_1)
                            _G_lookahead_2
                            """))



    def test_sequence(self):
        """
        Test generation of code for sequence patterns.
        """
        x = self.builder.exactly("x")
        y = self.builder.exactly("y")
        z = self.builder.sequence([x, y])
        self.assertEqual(writePython(z),
                         dd("""
                            _G_exactly_1 = self.exactly('x')
                            _G_exactly_2 = self.exactly('y')
                            _G_exactly_2
                            """))


    def test_bind(self):
        """
        Test code generation for variable assignment.
        """
        x = self.builder.exactly("x")
        b = self.builder.bind(x, "var")
        self.assertEqual(writePython(b),
                         dd("""
                            _G_exactly_1 = self.exactly('x')
                            _locals['var'] = _G_exactly_1
                            _locals['var']
                            """))


    def test_pred(self):
        """
        Test code generation for predicate expressions.
        """
        x = self.builder.pred(self.builder.exactly("x"))
        self.assertEqual(writePython(x),
                         dd("""
                            def _G_pred_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            _G_pred_2 = self.pred(_G_pred_1)
                            _G_pred_2
                            """))


    def test_action(self):
        """
        Test code generation for semantic actions.
        """
        x = self.builder.action("doStuff()")
        self.assertEqual(writePython(x),
                         dd("""
                            _G_python_1 = eval('doStuff()', self.globals, _locals)
                            """))


    def test_expr(self):
        """
        Test code generation for semantic predicates.
        """
        x = self.builder.expr("returnStuff()")
        self.assertEqual(writePython(x),
                         dd("""
                            _G_python_1 = eval('returnStuff()', self.globals, _locals)
                            _G_python_1
                            """))

    def test_listpattern(self):
        """
        Test code generation for list patterns.
        """
        x = self.builder.listpattern(self.builder.exactly("x"))
        self.assertEqual(writePython(x),
                         dd("""
                            def _G_listpattern_1():
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            _G_listpattern_2 = self.listpattern(_G_listpattern_1)
                            _G_listpattern_2
                            """))


    def test_rule(self):
        """
        Test generation of entire rules.
        """

        x = self.builder.rule("foo", self.builder.exactly("x"))
        self.assertEqual(writePython(x),
                         dd("""
                            def rule_foo(self):
                                _locals = {'self': self}
                                self.locals['foo'] = _locals
                                _G_exactly_1 = self.exactly('x')
                                return _G_exactly_1
                            """))


    def test_grammar(self):
        """
        Test generation of an entire grammar.
        """
        r1 = self.builder.rule("foo", self.builder.exactly("x"))
        r2 = self.builder.rule("baz", self.builder.exactly("y"))
        x = self.builder.makeGrammar([r1, r2])
        self.assertEqual(writePython(x),
                         dd("""
                            class BuilderTest(GrammarBase):
                                def rule_foo(self):
                                    _locals = {'self': self}
                                    self.locals['foo'] = _locals
                                    _G_exactly_1 = self.exactly('x')
                                    return _G_exactly_1


                                def rule_baz(self):
                                    _locals = {'self': self}
                                    self.locals['baz'] = _locals
                                    _G_exactly_1 = self.exactly('y')
                                    return _G_exactly_1
                            """))
