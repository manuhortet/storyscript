# -*- coding: utf-8 -*-
from .Ebnf import Ebnf


class Grammar:

    """
    Defines Storyscript's grammar using the Ebnf module, producing the complete
    EBNF grammar for it.
    """

    def __init__(self):
        self.ebnf = Ebnf()

    def macros(self):
        """
        Define the macros
        """
        collection = '{} (nl indent)? ({} (comma nl? {})*)? (nl dedent)? {}'
        self.ebnf.macro('collection', collection)
        self.ebnf.macro('simple_block', '{} nl nested_block')

    def types(self):
        """
        Defines available types
        """
        self.ebnf.INT_TYPE = 'int'
        self.ebnf.FLOAT_TYPE = 'float'
        self.ebnf.NUMBER_TYPE = 'number'
        self.ebnf.STRING_TYPE = 'string'
        self.ebnf.LIST_TYPE = 'list'
        self.ebnf.OBJECT_TYPE = 'object'
        self.ebnf.REGEXP_TYPE = 'regex'
        self.ebnf.FUNCTION_TYPE = 'function'
        self.ebnf.ANY_TYPE = 'any'
        rule = ('int_type, float_type, number_type, string_type, list_type, '
                'object_type, regexp_type, function_type, any_type')
        self.ebnf.types = rule

    def values(self):
        self.ebnf._NL = r'/(\r?\n[\t ]*)+/'
        self.ebnf._INDENT = '<INDENT>'
        self.ebnf._DEDENT = '<DEDENT>'
        self.ebnf.TRUE = 'true'
        self.ebnf.FALSE = 'false'
        self.ebnf.NULL = 'null'
        self.ebnf.set_token('RAW_INT.2', r'/[0-9]+/')
        self.ebnf.set_token('INT.2', '("+"|"-")? RAW_INT')
        self.ebnf.set_token('FLOAT.2', '("+"|"-")? INT "." RAW_INT? | '
                            '"." RAW_INT')
        self.ebnf.SINGLE_QUOTED = "/'([^']*)'/"
        self.ebnf.DOUBLE_QUOTED = '/"([^"]*)"/'
        self.ebnf.set_token('REGEXP.2', r'/\/([^\/]*)\//')
        self.ebnf.set_token('NAME.1', r'/[a-zA-Z-\/_0-9]+/')
        self.ebnf._OSB = '['
        self.ebnf._CSB = ']'
        self.ebnf._OCB = '{'
        self.ebnf._CCB = '}'
        self.ebnf._COLON = ':'
        self.ebnf._COMMA = ','
        self.ebnf._OP = '('
        self.ebnf._CP = ')'
        self.ebnf.boolean = 'true, false'
        self.ebnf.void = 'null'
        self.ebnf.number = 'int, float'
        self.ebnf.string = 'single_quoted, double_quoted'
        list = self.ebnf.collection('osb', 'expression', 'expression', 'csb')
        self.ebnf.set_rule('!list', list)
        self.ebnf.key_value = '(string, path) colon expression'
        objects = ('ocb', 'key_value', 'key_value', 'ccb')
        self.ebnf.objects = self.ebnf.collection(*objects)
        self.ebnf.regular_expression = 'regexp name?'
        self.ebnf.inline_expression = 'op service cp'
        values = ('number, string, boolean, void, list, objects, '
                  'regular_expression')
        self.ebnf.values = values

    def assignments(self):
        self.ebnf.EQUALS = '='
        self.ebnf._DOT = '.'
        path_fragment = 'dot name, osb int csb, osb string csb, osb path csb'
        self.ebnf.path_fragment = path_fragment
        self.ebnf.path = ('name (path_fragment)* | '
                          'inline_expression (path_fragment)*')
        assignment_fragment = 'equals (expression, service, mutation)'
        self.ebnf.assignment_fragment = assignment_fragment
        self.ebnf.assignment = 'path assignment_fragment'

    def imports(self):
        self.ebnf._AS = 'as'
        self.ebnf._IMPORT = 'import'
        self.ebnf.imports = 'import string as name'

    def expressions(self):

        self.ebnf.POWER = '^'
        self.ebnf.NOT = '!'

        self.ebnf.OR = 'or'
        self.ebnf.AND = 'and'

        self.ebnf.GREATER = '>'
        self.ebnf.GREATER_EQUAL = '>='
        self.ebnf.LESSER = '<'
        self.ebnf.LESSER_EQUAL = '<='
        self.ebnf.NOT_EQUAL = '!='
        self.ebnf.EQUAL = '=='

        self.ebnf.set_token('BSLASH.5', '/')
        self.ebnf.MULTIPLIER = '*'
        self.ebnf.set_token('MODULUS.5', '%')

        self.ebnf.set_token('PLUS.5', '+')
        self.ebnf.set_token('DASH.5', '-')

        self.ebnf.cmp_operator = ('GREATER, GREATER_EQUAL, LESSER, '
                                  'LESSER_EQUAL, NOT_EQUAL, EQUAL')
        self.ebnf.arith_operator = 'PLUS, DASH'
        self.ebnf.unary_operator = 'NOT'
        self.ebnf.mul_operator = 'MULTIPLIER, BSLASH, MODULUS'

        self.ebnf.primary_expression = 'entity , op or_expression cp'
        self.ebnf.pow_expression = ('primary_expression (POWER '
                                    'unary_expression)?')
        self.ebnf.unary_expression = ('unary_operator unary_expression , '
                                      'pow_expression')
        self.ebnf.mul_expression = '(mul_expression mul_operator)? ' \
                                   'unary_expression'
        self.ebnf.arith_expression = '(arith_expression arith_operator)? ' \
                                     'mul_expression'
        self.ebnf.cmp_expression = '(cmp_expression cmp_operator)? ' \
                                   'arith_expression'
        self.ebnf.and_expression = '(and_expression AND)? cmp_expression'
        self.ebnf.or_expression = '(or_expression OR)? and_expression'

        self.ebnf.expression = 'or_expression'
        self.ebnf.absolute_expression = 'expression'

    def raise_statement(self):
        self.ebnf.RAISE = 'raise'
        self.ebnf.raise_statement = ('raise entity?')

    def rules(self):
        self.ebnf.RETURN = 'return'
        self.ebnf.BREAK = 'break'
        self.ebnf.return_statement = 'return expression?'
        self.ebnf.break_statement = 'break'
        self.ebnf.entity = 'values, path'
        rules = ('absolute_expression, assignment, imports, return_statement, '
                 'raise_statement, break_statement, block')
        self.ebnf.rules = rules

    def mutation_block(self):
        self.ebnf._THEN = 'then'
        self.ebnf.mutation_fragment = 'name arguments*'
        self.ebnf.chained_mutation = 'then mutation_fragment'
        self.ebnf.mutation = 'entity (mutation_fragment (chained_mutation)*)'
        self.ebnf.mutation_block = 'mutation nl (nested_block)?'
        self.ebnf.indented_chain = 'indent (chained_mutation nl)+ dedent'

    def service_block(self):
        self.ebnf.command = 'name'
        self.ebnf.arguments = 'name? colon expression'
        self.ebnf.output = '(as name (comma name)*)'
        self.ebnf.service_fragment = '(command arguments*|arguments+) output?'
        self.ebnf.service = 'path service_fragment chained_mutation*'
        self.ebnf.service_block = 'service nl (nested_block)?'

    def if_block(self):
        self.ebnf._IF = 'if'
        self.ebnf._ELSE = 'else'
        self.ebnf.if_statement = 'if expression'
        elseif_statement = 'else if expression'
        self.ebnf.elseif_statement = elseif_statement
        self.ebnf.elseif_block = self.ebnf.simple_block('elseif_statement')
        self.ebnf.set_rule('!else_statement', 'else')
        self.ebnf.else_block = self.ebnf.simple_block('else_statement')
        if_block = 'if_statement nl nested_block elseif_block* else_block?'
        self.ebnf.if_block = if_block

    def while_block(self):
        self.ebnf._WHILE = 'while'
        self.ebnf.while_statement = 'while expression'
        self.ebnf.while_block = self.ebnf.simple_block('while_statement')

    def foreach_block(self):
        self.ebnf._FOREACH = 'foreach'
        self.ebnf.foreach_statement = 'foreach entity output'
        self.ebnf.foreach_block = self.ebnf.simple_block('foreach_statement')

    def function_block(self):
        self.ebnf._RETURNS = 'returns'
        self.ebnf.typed_argument = 'name colon types'
        self.ebnf.function_output = 'returns types'
        function_statement = ('function_type name typed_argument* '
                              'function_output?')
        self.ebnf.function_statement = function_statement
        self.ebnf.function_block = self.ebnf.simple_block('function_statement')

    def try_block(self):
        self.ebnf.TRY = 'try'
        self.ebnf._CATCH = 'catch'
        self.ebnf.FINALLY = 'finally'
        self.ebnf.catch_statement = 'catch as name'
        self.ebnf.catch_block = self.ebnf.simple_block('catch_statement')
        self.ebnf.finally_statement = 'finally'
        self.ebnf.finally_block = self.ebnf.simple_block('finally_statement')
        self.ebnf.try_statement = 'try'
        try_block = ('try_statement nl nested_block catch_block? '
                     'finally_block?')
        self.ebnf.try_block = try_block

    def block(self):
        self.ebnf._WHEN = 'when'
        when = 'when (path output|service)'
        self.ebnf.when_block = self.ebnf.simple_block(when)
        self.ebnf.indented_arguments = 'indent (arguments nl)+ dedent'
        block = ('rules nl, if_block, foreach_block, function_block, '
                 'arguments, indented_chain, chained_mutation, '
                 'mutation_block, service_block, when_block, try_block, '
                 'indented_arguments, while_block')
        self.ebnf.block = block
        self.ebnf.nested_block = 'indent block+ dedent'

    def build(self):
        self.ebnf._WS = '(" ")+'
        self.macros()
        self.types()
        self.values()
        self.assignments()
        self.imports()
        self.expressions()
        self.rules()
        self.mutation_block()
        self.service_block()
        self.if_block()
        self.foreach_block()
        self.while_block()
        self.function_block()
        self.try_block()
        self.raise_statement()
        self.block()
        self.ebnf.start = 'nl? block*'
        self.ebnf.ignore('_WS')
        return self.ebnf.build()
