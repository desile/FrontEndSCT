# -*- coding: utf-8 -*-
import re
import falcon
import json
import postgresql
from falcon_cors import CORS
from syntaxnet_wrapper import PipelineSyntaxNet
from api.tezaurus import getNormalForm

db = postgresql.open('pq://root:q1@localhost:5432/ruwordnet')

cors = CORS(allow_all_origins=True,
            allow_all_headers=True,
            allow_all_methods=True)


def print_result(result):
    for sent in result:
        for word in sent:
            print(word)
        print()


wordResultRegex = re.compile(r'(\d+) (\d+) \| word_form: (\S+) pos_tag: (\S+) morph: (\S+) parent (\S+) link_name: (\S+)')
morphGroupsRegex = re.compile(r'([^|\s]+=?[^\s^|]+)')

host = '127.0.0.1'
port = 8111  # E.g.

proc = PipelineSyntaxNet(host, port)

ADD_QUESTION_SQL = "INSERT INTO question (question) VALUES ($1) RETURNING id"
GET_ALL_QUESTIONS_SQL = "SELECT id, question, (SELECT count(*) from answer a where a.question_id = q.id) FROM question q"

ADD_ANSWER_SQL = "INSERT INTO answer (answer, question_id, etalon) VALUES ($1, $2, $3) RETURNING id"
GET_ANSWERS_BY_QUESTION = "SELECT id, answer, (SELECT count(*) from words_relation l where l.answer_id = a.id) FROM answer a WHERE $1 = a.question_id"

ADD_RELATION_SQL = "INSERT INTO words_relation (rel_name, weight, answer_id, group_number) VALUES ($1, $2, $3, $4) RETURNING id"
ADD_WORD_SQL = "INSERT INTO word (word, normal_form, pos, relation_id, position) VALUES ($1, $2, $3, $4, $5) RETURNING id"


GET_ALL_RELATIONS_BY_QUESTION_SQL = '''
    select wr.rel_name, wr.id, wr.weight, wr.group_number, wr.answer_id, array_agg(w.word), array_agg(w.normal_form), array_agg(w.pos), array_agg(w.position) from words_relation wr
      join answer a on wr.answer_id = a.id
      join word w on w.relation_id = wr.id
    where a.question_id = ($1)
    group by w.relation_id, wr.rel_name, wr.id, wr.weight, wr.group_number
'''


# TODO: Весь текст и связь между предложениями
def ud_parse(text):
    result = proc.process(text)
    for sent in result:
        sentenceResult = []
        for idx, word in enumerate(sent):
            m = wordResultRegex.match(str(word))
            if m:
                # Синтакснетовские поля
                wordResultDict = {}
                wordResultDict['id'] = idx
                wordResultDict['start_position'] = m.group(1)
                wordResultDict['end_position'] = m.group(2)
                wordResultDict['word'] = m.group(3)
                wordResultDict['pos_tag'] = m.group(4)
                wordResultDict['morph'] = dict(
                    (k, v) for k, v in (item.split('=') for item in morphGroupsRegex.findall(str(m.group(5)))))
                wordResultDict['parent_id'] = int(m.group(6))
                wordResultDict['link_name'] = m.group(7)
                # Находим нормальную форму слова
                wordResultDict['normal_form'] = getNormalForm(m.group(3), m.group(4))
                # Находим синонимы
                # synonym_query = db.query("SELECT sen2.name, syn.ruthes_name from senses sen join synsets syn on sen.synset_id = syn.id join senses sen2 on syn.id = sen2.synset_id where sen.name = '{}'".format(wordResultDict['normal_form'].replace('ё','е').upper()))
                # synonym_list = []
                # for synonym in synonym_query:
                #	synonym_list.append(synonym[0])
                # wordResultDict['synonyms'] = synonym_list
                sentenceResult.append(wordResultDict)
            else:
                raise ValueError("Cant parse SyntaxNet result: ", word)

        return sentenceResult


class QuestionResource(object):
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        question = req.json['question']
        addQuestionToDB = db.prepare(ADD_QUESTION_SQL)
        addQuestionToDB(question)

    def on_get(self, req, resp):
        questionQuery = db.query(GET_ALL_QUESTIONS_SQL)
        questionList = []
        for row in questionQuery:
            questionList.append({'id': row[0], 'question': row[1], 'answerCount': row[2]})
        resp.body = json.dumps(questionList)


class AnswerResource(object):
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        print(req.json)
        answer = req.json['answer']
        question_id = req.json['question_id']
        links = req.json['links']
        addAnswerToDB = db.prepare(ADD_ANSWER_SQL)
        answer_id = addAnswerToDB(answer, question_id)[0][0]
        for link in links:
            child_link = {}
            if link['child'] is not None:
                child_link['word'] = link['child']['word']
                child_link['normal_form'] = link['child']['normal_form']

            addLinkToDB = db.prepare(
                "INSERT INTO links (parent, parent_normal, child, child_normal, relation, weight, answer_id) VALUES ($1, $2, $3, $4, $5, $6, $7)")
            addLinkToDB(
                link['parent']['word'],
                link['parent']['normal_form'],
                child_link.get('word'),
                child_link.get('normal_form'),
                link['link'],
                float(link['weight']),
                answer_id
            )

    def on_get(self, req, resp):
        question_id = int(req.params['question_id'])
        answerList = []
        answerQuery = db.prepare(GET_ANSWERS_BY_QUESTION)
        for row in answerQuery(question_id):
            answerList.append({'id': row[0], 'answer': row[1], 'linkCount': row[2]})
        resp.body = json.dumps(answerList)


class CheckAnswerResource(object):
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        questionId = req.json['question_id']
        answer = req.json['answer']

        checkingLinks = []
        checkingWords = []
        sentenceResult = ud_parse(answer)
        for el in sentenceResult:
            if el['link_name'] != 'ROOT':
                checkingLinks.append({
                    'parent': sentenceResult[int(el['parent_id'])]['normal_form'],
                    'child': el['normal_form'],
                    'relation': el['link_name']
                })
                checkingWords.append(el['normal_form'])

        canonicalLinks = []
        fullWeight = 0
        linksQuery = db.prepare(
            'SELECT DISTINCT l.parent_normal, l.child_normal, l.relation, l.weight FROM links l JOIN answers a ON a.id = l.answer_id JOIN questions q ON q.id = a.question_id WHERE q.id = $1')
        for row in linksQuery(questionId):
            canonicalLinks.append({
                'parent': row[0],
                'child': row[1],
                'relation': row[2],
                'weight': row[3]
            })
            fullWeight += row[3]

        result = 0
        matches = []
        for canonicalLink in canonicalLinks:
            if canonicalLink['relation'] is None:
                for word in checkingWords:
                    if word.lower() == canonicalLink['parent'].lower():
                        result += canonicalLink['weight']
                        matches.append(canonicalLink)
            else:
                for checkingLink in checkingLinks:
                    # Нужно сравнивать нормальные формы приведенные к лоуверкейсу
                    if checkingLink['parent'].lower() == canonicalLink['parent'].lower():
                        if checkingLink['child'].lower() == canonicalLink['child'].lower():
                            if checkingLink['relation'] == canonicalLink['relation']:
                                result += canonicalLink['weight']
                                matches.append(canonicalLink)

        print(canonicalLinks)
        print(checkingLinks)
        resp.body = json.dumps({'result': result / fullWeight, 'matches': matches})


class BuildRelationsResource:
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        answers = req.json['answers']
        answers_relations = []
        # unique_answers_links = []
        for idx, answer in enumerate(answers):
            parsed_answer = ud_parse(answer)
            if len(parsed_answer) == 1:
                root = parsed_answer[0]
                answers_relations.append({
                    'words': [{'value': root['word'], 'normal_form': root['normal_form'], 'pos': root['pos_tag']}],
                    'relation': 'single',
                    'weight': 1.0,
                    'group': len(answers_relations),
                    'id': len(answers_relations),
                    'answer_id': idx
                })
            else:
                for word_with_syntax in parsed_answer:
                    if word_with_syntax['link_name'].lower() != 'root':
                        print(word_with_syntax)
                        new_relation = {
                            'relation': word_with_syntax['link_name'],
                            'weight': 1.0,
                            'group': len(answers_relations),
                            'id': len(answers_relations),
                            'answer_id': idx,
                            'words': [
                                {
                                    'value': word_with_syntax['word'],
                                    'normal_form': word_with_syntax['normal_form'],
                                    'pos': word_with_syntax['pos_tag']
                                },
                                {
                                    'value': parsed_answer[word_with_syntax['parent_id']]['word'],
                                    'normal_form': parsed_answer[word_with_syntax['parent_id']]['normal_form'],
                                    'pos': parsed_answer[word_with_syntax['parent_id']]['pos_tag']
                                }
                            ]
                        }
                        unique_relation = True
                        for relation in answers_relations:
                            if relation['relation'] == new_relation['relation']:
                                unique_relation = False
                                for i in range(0, len(relation['words'])):
                                    if relation['words'][i]['normal_form'] != new_relation['words'][i]['normal_form']:
                                        unique_relation = True

                        if unique_relation:
                            answers_relations.append(new_relation)

        answers_relations = [x for x in answers_relations if x['relation'].lower() != 'punct']

        resp.body = json.dumps(answers_relations)


class WizardSaveResource:
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        question = req.json['question']
        answers = req.json['answers']
        relations = req.json['relations']
        with db.xact():
            question_id = db.prepare(ADD_QUESTION_SQL)(question)[0][0]
            print(question_id)
            answer_ids = []
            for answer in answers:
                answer_ids.append(db.prepare(ADD_ANSWER_SQL)(answer, question_id, True)[0][0])
            print(answer_ids)
            for relation in relations:
                relation_id = db.prepare(ADD_RELATION_SQL)(
                    relation['relation'],
                    float(relation['weight']),
                    answer_ids[int(relation['answer_id'])],
                    int(relation['group'])
                )[0][0]
                for idx, word in enumerate(relation['words']):
                    db.prepare(ADD_WORD_SQL)(word['value'], word['normal_form'], word['pos'], relation_id, idx)


class SemanticResource(object):
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        text = req.json['text']
        sentenceResult = ud_parse(text)
        resp.body = json.dumps(sentenceResult)


class AllRelationsResource:
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        question_id = int(req.json['question_id'])
        relations_query = db.prepare(GET_ALL_RELATIONS_BY_QUESTION_SQL)
        relations = []
        for relation in relations_query(question_id):
            words = [{} for i in range(len(relation[8]))]
            for i in range(0, len(relation[8])):
                words[relation[8][i]] = ({
                    'value': relation[5][i],
                    'normal_form': relation[6][i],
                    'pos': relation[7][i]
                })
            relations.append({
                'relation': relation[0],
                'id': relation[1],
                'weight': relation[2],
                'group': relation[3],
                'answer_id': relation[4],
                'words': words
            })
        resp.body = json.dumps(relations)



api = falcon.API(middleware=[cors.middleware])
api.add_route('/parse', SemanticResource())
api.add_route('/build_relations', BuildRelationsResource())
api.add_route('/relations/all', AllRelationsResource())
api.add_route('/wizard_save', WizardSaveResource())
api.add_route('/questions', QuestionResource())
api.add_route('/answers', AnswerResource())
api.add_route('/answer/check', CheckAnswerResource())
