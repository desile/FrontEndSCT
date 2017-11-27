import re

class SyntaxNode:

    morphGroupsRegex = re.compile(r'([^|\s]+=?[^\s^|]+)')

    def __init__(self, idx, start_position, end_position, word, morph_raw, parent=None, parent_id=None, link_name=None):
        self._id = idx,
        self._start_position = start_position
        self._end_position = end_position
        self._word = word
        self._morph = dict(
            (k, v) for k, v in (item.split('=') for item in self.morphGroupsRegex.findall(str(morph_raw))))
        self._parent = parent
        self._parent_id = parent_id
        self._children = []
        self._link_name = link_name

    def set_parent(self, parent):
        self._parent = parent
        parent.register_child(self)

    def register_child(self, child):
        self._children.append(child)

    def get_id(self):
        return self._id

    def get_word(self):
        return self._word

    def get_children(self):
        return self._children

    def get_parent(self):
        return self._parent

    def get_parent_id(self):
        return self._parent_id

    def get_link(self):
        return self._link_name
