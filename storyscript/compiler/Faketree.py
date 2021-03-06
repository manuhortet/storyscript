# -*- coding: utf-8 -*-
from lark.lexer import Token

from ..parser import Tree


class FakeTree:
    """
    Creates fake trees that are not in the original story source.
    """
    def __init__(self, block):
        self.block = block
        self.original_line = str(block.line())
        self.new_lines = {}

    def line(self):
        """
        Creates fake line numbers. The strings are decreasingly sorted,
        so that the resulting tree is compiled correctly.
        """
        line = self.original_line
        parts = line.split('.')
        if len(parts) > 1:
            line = '.'.join(parts[:-1])
        # We start at .1, s.t. lines from L1 are called L1.1 and not L1.0
        # to avoid any potential confusion
        new_suffix = len(self.new_lines) + 1
        fake_line = f'{line}.{new_suffix}'
        self.new_lines[fake_line] = None
        return fake_line

    def get_line(self, tree):
        """
        Gets the tree line if it's a new one, otherwise creates it.
        """
        if tree.line() in self.new_lines:
            return tree.line()
        return self.line()

    def path(self, name=None, line=None):
        """
        Creates a fake tree path.
        """
        if line is None:
            line = self.line()
        if name is None:
            name = f'p-{line}'
        return Tree('path', [Token('NAME', name, line=line)])

    def assignment(self, value):
        """
        Creates a fake assignment tree, equivalent to "$fake = value"
        """
        line = self.get_line(value)
        value.child(0).child(0).line = line
        path = self.path(line=line)
        equals = Token('EQUALS', '=', line=line)
        fragment = Tree('assignment_fragment', [equals, value])
        return Tree('assignment', [path, fragment])

    def add_assignment(self, value):
        """
        Creates an assignments and adds it to the current block
        """
        assignment = self.assignment(value)
        if self.block.child(1):
            children = [self.block.child(0), assignment, self.block.child(1)]
            self.block.children = children
        else:
            self.block.children = [assignment, self.block.child(0)]
        return assignment
