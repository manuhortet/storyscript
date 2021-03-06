# -*- coding: utf-8 -*-
import io

from lark import Lark

from pytest import fixture

from storyscript.parser import (CustomIndenter, Grammar, Parser, Transformer,
                                Tree)


@fixture
def parser():
    return Parser()


def test_parser_init(parser):
    assert parser.algo == 'lalr'
    assert parser.ebnf is None


def test_parser_init_algo():
    parser = Parser(algo='algo')
    assert parser.algo == 'algo'


def test_parser_init_ebnf():
    parser = Parser(ebnf='grammar.ebnf')
    assert parser.ebnf == 'grammar.ebnf'


def test_parser_indenter(patch):
    patch.init(CustomIndenter)
    assert isinstance(Parser.indenter(), CustomIndenter)


def test_parser_transfomer(patch):
    patch.init(Transformer)
    result = Parser.transformer()
    assert isinstance(result, Transformer)


def test_parser_grammar(patch, parser):
    patch.init(Grammar)
    patch.object(Grammar, 'build')
    result = parser.grammar()
    assert Grammar.__init__.call_count == 1
    assert result == Grammar().build()


def test_parser_grammar_ebnf(patch, parser):
    patch.object(io, 'open')
    parser.ebnf = 'test.ebnf'
    result = parser.grammar()
    io.open.assert_called_with('test.ebnf', 'r')
    assert result == io.open().__enter__().read()


def test_parser_lark(patch, parser):
    """
    Ensures Parser.lark can produce the correct Lark instance.
    """
    patch.init(Lark)
    patch.many(Parser, ['indenter', 'grammar'])
    result = parser.lark()
    kwargs = {'parser': parser.algo, 'postlex': Parser.indenter()}
    Lark.__init__.assert_called_with(parser.grammar(), **kwargs)
    assert isinstance(result, Lark)


def test_parser_parse(patch, parser):
    """
    Ensures the build method can build the grammar
    """
    patch.many(Parser, ['lark', 'transformer'])
    result = parser.parse('source')
    Parser.lark().parse.assert_called_with('source\n')
    Parser.transformer().transform.assert_called_with(Parser.lark().parse())
    assert result == Parser.transformer().transform()


def test_parser_parse_empty(patch, parser):
    """
    Ensures that empty stories are parsed correctly
    """
    assert parser.parse('') == Tree('empty', [])


def test_parser_lex(patch, parser):
    patch.many(Parser, ['lark', 'indenter'])
    result = parser.lex('source')
    Parser.lark().lex.assert_called_with('source')
    assert result == Parser.lark().lex()
