# coding=utf-8
import postgresql
import pymorphy2

tezaurus = 'tezaurus'
morph = pymorphy2.MorphAnalyzer()
db = postgresql.open('pq://root:q1@localhost:5432/ruwordnet')

# TODO: Более точная логика разбора
UDtoOCgrammems = {
    # NOUN - Имя существительное
    'NOUN': ['NOUN'],
    # ADJF - Имя прилагательное полное. Имеет Degree: Pos (positive, first degree)
    # ADJV - Имя прилигательное краткое. Имеет Variant: Brev / Short (short form of adjectives)
    # COMP - Компаратив. Имеет Degree: Cmp
    'ADJ': ['ADJF', 'ADJS', 'COMP'],
    'DET': ['ADJF'],  # determiner (указательное местоимение)
    # VERB - Личная форма глагола. Имеет VerbForm: Fin (finitive)
    # INFN - Инфинитив. Имеет VerbForm: Inf (infinitive)
    # PRTF - Полное причастие. Имеет VerbForm: Part (participle)
    # PRTS - Краткое причастие. Имеет VerbForm: Part и Variant: Brev / Short
    # GRND - Деепричастие. Имеет VerbForm: Trans
    'VERB': ['VERB', 'INFN', 'PRTF', 'PRTS', 'GRND'],
    'AUX': ['VERB'],  # auxiliary verb (быть)
    # NUM - Числительное
    'NUM': ['NUMR'],
    # ADVB - Наречение
    'ADV': ['ADVB'],
    # NPRO - Местоимение-существительное
    'PRON': ['NPRO'],
    # PREP - Предлог
    'ADP': ['PREP'],
    # CONJ - Союз
    'CONJ': ['CONJ'],
    'SCONJ': ['CONJ'],  # subordinating conjuction (условные союзы)
    # PRCL - Частица
    'PART': ['PRCL'],
    'PUNCT': ['PUNCT']
}


def getNormalForm(word, POStag):
    parsedVariants = morph.parse(word)
    for parsed in parsedVariants:
        if parsed.tag.POS in UDtoOCgrammems[POStag]:
            return parsed.normal_form
    return parsedVariants[0].normal_form


def getSynonyms(word):
    word = word.replace('ё', 'е').upper()
    synonym_query = db.query('''
		SELECT sen2.name, syn.ruthes_name from senses sen 
		join synsets syn on sen.synset_id = syn.id 
		join senses sen2 on syn.id = sen2.synset_id 
		where sen.name = '{}' '''.format(word))
    synonym_list = []
    for synonym in synonym_query:
        synonym_list.append(synonym[0])


def getDomen(word):
    word = word.replace('ё', 'е').upper()
    domen_query = db.query('''
		SELECT sen2.name, syn2.ruthes_name 
		from senses sen
		 join synsets syn on sen.synset_id = syn.id
		 join relations rel on syn.id = rel.parent_id
		 join synsets syn2 on syn2.id = rel.child_id
		 join senses sen2 on syn2.id = sen2.synset_id
		where sen.name = '{}' and rel.name = '{}'
	'''.format(word, 'domain'))
    domen_list = []
    for domen in domen_query:
        domen_list.append(domen[0])
