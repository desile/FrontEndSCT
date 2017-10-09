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


# TODO: Весь текст и связь между предложениями
def parseAndAnalyze(text):
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
                wordResultDict['parent_id'] = m.group(6)
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
        addQuestionToDB = db.prepare("INSERT INTO questions (question) VALUES ($1)")
        addQuestionToDB(question)

    def on_get(self, req, resp):
        questionQuery = db.query(
            'SELECT id, question, (SELECT count(*) from answers a where a.question_id = q.id) FROM questions q')
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
        addAnswerToDB = db.prepare("INSERT INTO answers (answer, question_id) VALUES ($1, $2) RETURNING id")
        answer_id = addAnswerToDB(answer, question_id)[0][0]
        for link in links:
            child_link = {}
            if link['child'] is not None:
                child_link['word'] = link['child']['word']
                child_link['normal_form'] = link['child']['normal_form']

            addLinkToDB = db.prepare(
                "INSERT INTO links (parent, parent_normal, child, child_normal, relation, weight, answer_id) VALUES ($1, $2, $3, $4, $5)")
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
        answerQuery = db.prepare(
            'SELECT id, answer, (SELECT count(*) from links l where l.answer_id = a.id) FROM answers a WHERE $1 = a.question_id')
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
        sentenceResult = parseAndAnalyze(answer)
        for el in sentenceResult:
            if el['link_name'] != 'ROOT':
                checkingLinks.append({
                    'parent': sentenceResult[int(el['parent_id'])]['word'],
                    'child': el['word'],
                    'relation': el['link_name']
                })
                checkingWords.append(el['word'])

        canonicalLinks = []
        fullWeight = 0
        linksQuery = db.prepare(
            'SELECT l.parent, l.child, l.relation, l.weight FROM links l JOIN answers a ON a.id = l.answer_id JOIN questions q ON q.id = a.question_id WHERE q.id = $1')
        for row in linksQuery(questionId):
            canonicalLinks.append({
                'parent': row[0],
                'child': row[1],
                'relation': row[2],
                'weight': row[3]
            })
            fullWeight += row[3]

        result = 0
        for canonicalLink in canonicalLinks:
            if canonicalLink['relation'] is None:
                for word in checkingWords:
                    if word == canonicalLink['parent']:
                        result += canonicalLink['weight']
            else:
                for checkingLink in checkingLinks:
                    # Нужно сравнивать нормальные формы приведенные к лоуверкейсу
                    if checkingLink['parent'] == canonicalLink['parent']:
                        if checkingLink['child'] == canonicalLink['child']:
                            if checkingLink['relation'] == canonicalLink['relation']:
                                result += canonicalLink['weight']

        print(canonicalLinks)
        print(checkingLinks)
        resp.body = json.dumps({'result': result / fullWeight})


class SemanticResource(object):
    def on_post(self, req, resp):
        req.json = json.loads(req.stream.read().decode('UTF-8'))
        text = req.json['text']
        sentenceResult = parseAndAnalyze(text)
        resp.body = json.dumps(sentenceResult)


api = falcon.API(middleware=[cors.middleware])
api.add_route('/parse', SemanticResource())
api.add_route('/questions', QuestionResource())
api.add_route('/answers', AnswerResource())
api.add_route('/answer/check', CheckAnswerResource())
