from api.tezaurus import getNormalForm


class Word:

    def __init__(self, word, pos_tag):
        self._value = word
        self._pos_tag = pos_tag
        self._normal_form = getNormalForm(word, pos_tag)

    def get(self):
        return self._value

    def pos(self):
        return self._pos_tag

    def normal_form(self):
        return self._normal_form
