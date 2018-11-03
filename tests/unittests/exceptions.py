# -*- coding: utf-8 -*-
import os

from pytest import fixture

from storyscript.exceptions import StoryError


@fixture
def error(magic):
    return StoryError('unknown', magic(spec=['line', 'column']))


def test_exceptions_storyerror_init():
    error = StoryError('unknown', 'item')
    assert error.error_type == 'unknown'
    assert error.item == 'item'
    assert error.path is None
    assert issubclass(StoryError, SyntaxError)


def test_exceptions_storyerror_init_path():
    error = StoryError('unknown', 'item', path='hello.story')
    assert error.error_type == 'unknown'
    assert error.item == 'item'
    assert error.path == 'hello.story'
    assert issubclass(StoryError, SyntaxError)


def test_exceptions_storyerror_escape_string(magic):
    string = magic()
    assert StoryError.escape_string(string) == string.encode().decode()


def test_exceptions_storyerror_reason(error):
    error.error_type = 'service-path'
    assert error.reason() == StoryError.reasons['service-path']


def test_exceptions_storyerror_noreason(error):
    assert error.reason() == 'unknown'


def test_exceptions_storyerror_name(error):
    assert error.name() == 'story'


def test_exceptions_storyerror_name_path(error):
    error.path = 'hello.story'
    assert error.name() == 'story "hello.story"'


def test_exceptions_storyerror_name_abspath(patch, error):
    """
    Ensures that paths are simplified for stories in the current working
    directory.
    """
    patch.object(os, 'getcwd', return_value='/abspath')
    error.path = '/abspath/hello.story'
    assert error.name() == 'story "hello.story"'


def test_exceptions_storyerror_token_template(patch, error):
    patch.object(StoryError, 'name')
    expected = ('Failed reading {} because of unexpected "value" at '
                'line 1, column 2').format(StoryError.name())
    assert error.token_template('value', 1, 2) == expected


def test_exceptions_storyerror_tree_template(patch, error):
    patch.object(StoryError, 'name')
    expected = ('Failed reading {} because of unexpected "value" at '
                'line 1').format(StoryError.name())
    assert error.tree_template('value', 1) == expected


def test_exceptions_storyerror_compile_template(patch, error):
    patch.object(StoryError, 'token_template')
    result = error.compile_template()
    args = (error.item, error.item.line, error.item.column)
    StoryError.token_template.assert_called_with(*args)
    assert result == StoryError.token_template()


def test_exceptions_storyerror_compile_template_error(patch, magic, error):
    """
    Ensures compile_template can handle UnexpectedToken items.
    """
    patch.object(StoryError, 'token_template')
    error.item.token = magic()
    result = error.compile_template()
    args = (error.item.token.value, error.item.line, error.item.column)
    StoryError.token_template.assert_called_with(*args)
    assert result == StoryError.token_template()


def test_exceptions_storyerror_compile_template_input(patch, magic, error):
    """
    Ensures compile_template can handle UnexpectedInput items.
    """
    patch.object(StoryError, 'token_template')
    error.item.context = 'context'
    result = error.compile_template()
    args = (error.item.context, error.item.line, error.item.column)
    StoryError.token_template.assert_called_with(*args)
    assert result == StoryError.token_template()


def test_exceptions_storyerror_compile_template_tree(patch, error):
    patch.object(StoryError, 'tree_template')
    error.item.data = 'data'
    result = error.compile_template()
    args = (error.item, error.item.line())
    StoryError.tree_template.assert_called_with(*args)
    assert result == StoryError.tree_template()


def test_exceptions_storyerror_compile_template_dict(patch, error):
    """
    Ensures compile_template can handle dictionary items.
    """
    patch.object(StoryError, 'tree_template')
    error.item = {'value': 'value', 'line': '1'}
    result = error.compile_template()
    StoryError.tree_template.assert_called_with('value', '1')
    assert result == StoryError.tree_template()


def test_exceptions_storyerror_message(patch, error):
    patch.many(StoryError, ['compile_template', 'escape_string'])
    result = error.message()
    StoryError.escape_string.assert_called_with(StoryError.compile_template())
    assert result == StoryError.escape_string()


def test_exceptions_storyerror_message_reason(patch, error):
    patch.many(StoryError, ['compile_template', 'escape_string', 'reason'])
    error.error_type = 'else'
    result = error.message()
    args = (StoryError.escape_string(), StoryError.reason())
    assert result == '{}. Reason: {}'.format(*args)


def test_exceptions_storyerror_echo(capsys, patch, error):
    """
    Ensures StoryError.echo print StoryError.message
    """
    patch.object(StoryError, 'message')
    error.echo()
    output, error = capsys.readouterr()
    assert output == '{}\n'.format(StoryError.message())


def test_exceptions_storyerror_str_(patch, error):
    patch.object(StoryError, 'message', return_value='pretty')
    assert str(error) == StoryError.message()
