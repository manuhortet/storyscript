# -*- coding: utf-8 -*-
import os

import click

from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from .CompilerError import CompilerError
from ..ErrorCodes import ErrorCodes
from ..Intention import Intention


class StoryError(SyntaxError):

    """
    Handles story-related errors (reading, parsing, compiling), transforming
    raw errors in nice and helpful messages.
    """

    def __init__(self, error, story, path=None):
        self.error = error
        self.story = story
        self.path = path
        self.error_tuple = None
        self.with_color = True

    def name(self):
        """
        Extracts the name of the story from the path.
        """
        if self.path:
            working_directory = os.getcwd()
            if self.path.startswith(working_directory):
                return self.path[len(working_directory) + 1:]
            return self.path
        return 'story'

    def get_line(self):
        """
        Gets the error line
        """
        return self.story.splitlines(keepends=False)[int(self.error.line) - 1]

    def header(self):
        """
        Creates the header of the message
        """
        template = 'Error: syntax error in {} at line {}, column {}'
        name = self.name()
        if self.with_color:
            name = click.style(self.name(), bold=True)
        return template.format(name, self.error.line, self.error.column)

    def symbols(self):
        """
        Creates the repeated symbols that mark the error.
        """
        end_column = int(self.error.column) + 1
        if hasattr(self.error, 'end_column'):
            end_column = int(self.error.end_column)
        symbols = '^' * (end_column - int(self.error.column))
        if self.with_color:
            return click.style(symbols, fg='red')
        else:
            return symbols

    def highlight(self):
        """
        Creates the error highlight of the message
        """
        spaces = ' ' * (int(self.error.column) + 5)
        highlight = '{}{}'.format(spaces, self.symbols())
        line = self.error.line
        return '{}|    {}\n{}'.format(line, self.get_line(), highlight)

    def error_code(self):
        """
        Provides the error code for the current error.
        """
        return self.error_tuple[0]

    def hint(self):
        """
        Provides an hint for the current error.
        """
        if self.error_tuple == ErrorCodes.unidentified_error:
            if hasattr(self.error, 'message'):
                return self.error.message()
            else:
                return str(self.error)
        if self.error_tuple == ErrorCodes.invalid_character:
            return self.error_tuple[1].format(
                    self.get_line()[self.error.column - 1])
        elif self.error_tuple == ErrorCodes.function_already_declared:
            extra = self.error.extra
            return self.error_tuple[1].format(extra.function_name,
                                              extra.previous_line)
        elif self.error_tuple == ErrorCodes.unexpected_token:
            token = self.error.token
            expected = str(self.error.expected)
            return self.error_tuple[1].format(token, expected)
        return self.error_tuple[1]

    def unexpected_token_code(self):
        """
        Finds the error code when the error is UnexpectedToken
        """
        intention = Intention(self.get_line())
        if intention.assignment():
            return ErrorCodes.assignment_incomplete
        elif intention.unnecessary_colon():
            return ErrorCodes.unnecessary_colon
        elif self.error.expected == ['_INDENT']:
            return ErrorCodes.block_expected_after
        return ErrorCodes.unexpected_token

    @staticmethod
    def is_valid_name_start(token):
        return token.isalpha() or token == '_'

    def unexpected_characters_code(self):
        """
        Finds the error code when the error is UnexpectedCharacters
        """
        line = self.get_line()
        error_column = line[self.error.column - 1]
        intention = Intention(line)
        if intention.is_function():
            return ErrorCodes.function_misspell
        elif intention.unnecessary_colon():
            return ErrorCodes.unnecessary_colon
        elif self.error.allowed is None and \
                self.is_valid_name_start(error_column):
            return ErrorCodes.block_expected_before

        return ErrorCodes.invalid_character

    def identify(self):
        """
        Identifies the error.
        """
        if hasattr(self.error, 'error'):
            if not isinstance(self.error.error, str):
                return ErrorCodes.unidentified_error
            if ErrorCodes.is_error(self.error.error):
                return ErrorCodes.get_error(self.error.error)

        if isinstance(self.error, UnexpectedToken):
            return self.unexpected_token_code()
        elif isinstance(self.error, UnexpectedCharacters):
            return self.unexpected_characters_code()
        return ErrorCodes.unidentified_error

    def process(self):
        """
        Process the error, assigning the error code and performing other
        operations when necessary.
        """
        self.error_tuple = self.identify()

    def message(self):
        """
        Creates a friendly error message.
        """
        self.process()
        # Check whether the error comes with source information
        if hasattr(self.error, 'line'):
            args = (self.header(), self.highlight(),
                    self.error_code(), self.hint())
            return '{}\n\n{}\n\n{}: {}'.format(*args)
        else:
            return self.error.message()

    def short_message(self):
        """
        A short version of the error message
        """
        self.process()
        return f'{self.error_code()}: {self.hint()}'

    def echo(self):
        """
        Prints the message
        """
        click.echo(self.message())

    @staticmethod
    def unnamed_error(message):
        return StoryError(CompilerError(None, message=message), None)

    @staticmethod
    def internal_error(error):
        url = 'https://github.com/storyscript/storyscript/issues'
        message = 'Internal error occured: {}\nPlease report at {}'
        return StoryError.unnamed_error(message.format(error, url))
