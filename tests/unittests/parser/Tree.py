# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from pytest import fixture, mark, raises

from storyscript.exceptions.CompilerError import CompilerError
from storyscript.parser import Tree


@fixture
def tree():
    return Tree('data', [])


@fixture
def dictionary():
    return {'script': {}}


def test_tree():
    assert issubclass(Tree, LarkTree)


def test_tree_walk():
    inner_tree = Tree('inner', [])
    tree = Tree('rule', [inner_tree])
    result = Tree.walk(tree, 'inner')
    assert result == inner_tree


def test_tree_walk_token():
    """
    Ensures that encountered tokens are skipped
    """
    inner_tree = Tree('inner', [])
    tree = Tree('rule', [Token('test', 'test'), inner_tree])
    result = Tree.walk(tree, 'inner')
    assert result == inner_tree


def test_tree_node(patch):
    patch.object(Tree, 'walk')
    tree = Tree('rule', [])
    result = tree.node('inner')
    Tree.walk.assert_called_with(tree, 'inner')
    assert result == Tree.walk()


def test_tree_child():
    tree = Tree('rule', ['child'])
    assert tree.child(0) == 'child'


def test_tree_child_overflow():
    tree = Tree('rule', ['child'])
    assert tree.child(1) is None


def test_tree_line():
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', line=1)])])
    assert tree.line() == '1'


def test_tree_column():
    """
    Ensures Tree.column can find the column of a tree
    """
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', column=1)])])
    assert tree.column() == '1'


def test_tree_end_column():
    """
    Ensures Tree.end_column can find the end column of a tree.
    """
    token = Token('WORD', 'word')
    token.end_column = 1
    tree = Tree('outer', [Tree('path', [token])])
    assert tree.end_column() == '1'


def test_tree_insert():
    tree = Tree('tree', [])
    tree.insert('child')
    assert tree.children == ['child']


def test_tree_rename():
    """
    Ensures Tree.rename can rename the current tree
    """
    tree = Tree('tree', [])
    tree.rename('new')
    assert tree.data == 'new'


def test_tree_replace():
    tree = Tree('tree', ['old'])
    tree.replace(0, 'new')
    assert tree.children == ['new']


def test_tree_extract_path():
    tree = Tree('path', [Token('NAME', 'one')])
    assert tree.extract_path() == 'one'


def test_tree_extract_path_fragments():
    subtree = Tree('fragment', [Token('NAME', 'two')])
    tree = Tree('path', [Token('NAME', 'one'), subtree, subtree])
    assert tree.extract_path() == 'one.two.two'


def test_tree_attributes(patch):
    patch.object(Tree, 'node')
    tree = Tree('master', [])
    result = tree.branch
    Tree.node.assert_called_with('branch')
    assert result == Tree.node()


def test_tree_find():
    """
    Ensures Tree.find can find the correct subtree.
    """
    expected = Tree('assignment', ['x'])
    tree = Tree('start', [Tree('block', [Tree('line', [expected])])])
    assert tree.find('assignment') == [expected]


def test_tree_extract():
    target = Tree('target', [])
    tree = Tree('tree', [target, Tree('more', [target])])
    assert tree.extract('target') == [target]


def test_tree_is_unary_leaf():
    """
    Ensures is_unary_leaf can find out whether an expression is unary leaf
    """
    tree = Tree('expression', [
        Tree('or_expression', [
            Tree('and_expression', [
                Tree('cmp_expression', [
                    Tree('arith_expression', [
                        Tree('mul_expression', [
                            Tree('unary_expression', [
                                Tree('pow_expression', [
                                    Tree('primary_expression', [
                                        Tree('entity', [
                                            Tree('values', [
                                                0
                                            ])
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ])
    assert tree.is_unary_leaf() is True


@mark.parametrize('tree', [
    Tree('any', []),
    Tree('arith_expression', [1, 2]),
    Tree('arith_expression', [Tree('unary_expression', [1, 2])]),
    Tree('arith_expression',
         [Tree('unary_expression', [Tree('pow_expression', [1, 2])])]),
    Tree('arith_expression',
         [Tree('unary_expression',
               [Tree('pow_expression',
                     [Tree('primary_expression', [1, 2])])])]),
])
def test_tree_is_unary_leaf_false(tree):
    """
    Ensures is_unary returns False when the tree is not an unary
    """
    assert tree.is_unary_leaf() is False


def test_tree_expect(tree):
    """
    Ensures expect throws an error
    """
    with raises(CompilerError) as e:
        tree.expect(0, 'error')

    assert e.value.message() == 'Unknown compiler error'


def test_follow_node_chain_no_children(tree):
    """
    Ensures we don't follow a node chain if there are no children
    """
    assert tree.follow_node_chain(['foo', 'bar']) is None
    tree.children = [1, 2]
    assert tree.follow_node_chain(['foo', 'bar']) is None


def test_follow_node_chain_children(patch, tree):
    """
    Ensures we follow a node chain if there are children
    """
    m = Tree('mock', [])
    tree.children = [0]
    patch.object(Tree, 'iter_subtrees')
    Tree.iter_subtrees.return_value = iter([m])
    assert tree.follow_node_chain(['foo', 'bar']) is None

    Tree.iter_subtrees.return_value = iter([m])
    assert tree.follow_node_chain(['mock']) is m

    arr = [m, Tree('m2', []), Tree('m3', [])]
    Tree.iter_subtrees.side_effect = lambda: iter(arr)
    assert tree.follow_node_chain(['mock']) is None
    assert tree.follow_node_chain(['mock', 'm2']) is None
    assert tree.follow_node_chain(['m2', 'mock']) is None
    assert tree.follow_node_chain(['m4', 'm2', 'mock']) is None
    assert tree.follow_node_chain(['m4', 'm3', 'm2', 'mock']) is None
    assert tree.follow_node_chain(['m3', 'm2', 'mock']) == m
