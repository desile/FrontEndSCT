import re

from udparser.SyntaxNode import SyntaxNode
from udparser.Word import Word


class SyntaxTree:

    _wordResultRegex = re.compile(r'(\d+) (\d+) \| word_form: (\S+) pos_tag: (\S+) morph: (\S+) parent (\S+) link_name: (\S+)')

    def __init__(self, root, nodes_dict=None):
        self._root = root
        self._nodes = nodes_dict
        pass

    @staticmethod
    def build_tree_from_raw_ud(self, ud_sentence):
        sentenceResult = {}
        for idx, word in enumerate(ud_sentence):
            m = self._wordResultRegex.match(str(word))
            if m:
                # Синтакснетовские поля
                wordResultDict = {}
                wordResultDict['id'] = idx
                wordResultDict['start_position'] = m.group(1)
                wordResultDict['end_position'] = m.group(2)
                wordResultDict['word'] = Word(m.group(3), m.group(4))
                wordResultDict['morph'] = m.group(5)
                wordResultDict['parent_id'] = int(m.group(6))
                wordResultDict['link_name'] = m.group(7)
                sentenceResult[idx] = wordResultDict
            else:
                raise ValueError("Cant parse SyntaxNet result: ", word)

        nodes_dict = {}
        for idx, value in sentenceResult:
            nodes_dict[idx] = SyntaxNode(idx,
                       value['start_position'],
                       value['end_position'],
                       value['word'],
                       value['morph'],
                       link_name=value['link_name'],
                       parent_id=value['parent_id'])

        root_idx = None
        for idx, value in nodes_dict:
            parent_id = nodes_dict[idx]._parent_id
            if value['parent_id'] < 0:
                root_idx = idx
            else:
                nodes_dict[idx].set_parent(nodes_dict[parent_id])

        return SyntaxTree(nodes_dict[root_idx], nodes_dict=nodes_dict)

    def get_root(self):
        return self._root

    def get_all_nodes(self):
        return self._nodes
