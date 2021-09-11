class Node:
    def __init__(self, value=None, left=None, right=None, parent=None):
        self.value = value
        self.__parent = parent
        self.__left = left
        self.__right = right

    @property
    def has_children(self):
        return self.left or self.right

    @property
    def left(self):
        return self.__left

    @left.setter
    def left(self, x):
        self.__left = x
        x.parent = self

    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, x):
        self.__right = x
        x.parent = self

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, x):
        self.__parent = x

    def __gt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return '%s' % self.value


class HuffmanLeaf(Node):
    def __init__(self, prob=None, word=None, code=None):
        super().__init__(prob, None, None)
        self.word = word
        self.code = code

    def __str__(self):
        return '<value: %s, word: %s, code: %s>' % (self.value, self.word, self.code)
